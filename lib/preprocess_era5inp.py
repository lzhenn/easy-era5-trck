#/usr/bin/env python
"""Preprocessing the ERA5 input file"""

import configparser
import datetime
import numpy as np
import pandas as pd
import xarray as xr
import gc
import os
import lib.utils as utils


print_prefix='lib.preprocess_era5inp>>'

class era5_acc_fields:

    '''
    Construct and accumulate U V W field 
    

    Attributes
    -----------
    forward: int
        1   -- forward integral
        -1  -- backward integral

    strt_t: datetime
        initial time for integration. Example:

                    00:00   ---> 06:00
        forward     strt_t  ---> final_t
        backward    final_t ---> strt_t

    final_t: datetime
        final time for integration 

    era5_dt: int
        input data frq from era5 raw input file(s), in seconds

    nc_files: list[str]
        string list of all file names that will be used to read wind fields

    drv_fld_dt: int
        time interval (in seconds) of driving fields (not interval of input files)

    U: float
        zonal wind
    
    V: float
        meridional wind

    W: float
        verticle velocity (Pa/s)
    
    xlon: float
        longitude 1d

    xlat: float
        latitude 1d

    xz: float
        isobaricInhPa 1d

    Methods
    '''
    
    def __init__(self, config):
        """ construct input era5 file names """
        fn_suffix='-pl.grib'
        utils.write_log(print_prefix+' IO initiate...')
        
        self.strt_t=datetime.datetime.strptime(config['CORE']['start_ymdh'], '%Y%m%d%H')

        self.forward=int(config['CORE']['forward_option'])
        self.final_t=self.strt_t+datetime.timedelta(hours=self.forward*int(config['CORE']['integration_length']))


        input_dir=config['INPUT']['input_era5_case']
        fn=input_dir+'/'+self.strt_t.strftime('%Y%m%d')+fn_suffix
        self.nc_pres_files=[fn]
        
        # read the first file
        utils.write_log(print_prefix+fn+' Reading...')
        if not(os.path.exists(fn)):
            utils.throw_error(print_prefix+'cannot locate:'+fn+', please check files or settings!')

        ds_grib = [xr.load_dataset(fn, engine='cfgrib', backend_kwargs={'errors': 'ignore'})]
        
        # read following files
        fn_dt=datetime.timedelta(days=1*self.forward) 
        curr_t= self.strt_t
        while curr_t.strftime('%Y%m%d') != self.final_t.strftime('%Y%m%d'):
            curr_t=curr_t+fn_dt
            fn=input_dir+'/'+curr_t.strftime('%Y%m%d')+fn_suffix
            utils.write_log(print_prefix+fn+' Reading...')
            
            if not(os.path.exists(fn)):
                utils.throw_error(print_prefix+'cannot locate:'+fn+', please check files or settings!')
            self.nc_pres_files.append(fn) 
            ds_grib.append(xr.load_dataset(fn, engine='cfgrib', backend_kwargs={'errors': 'ignore'}))
         
        if self.forward == -1:
            utils.write_log(print_prefix+' prepare for BACKWARD integration...')
            ds_grib=ds_grib[::-1]
            slice_start=self.final_t
            slice_end=self.strt_t

        elif self.forward == 1:
            utils.write_log(print_prefix+' prepare for FORWARD integration...')
            slice_start=self.strt_t
            slice_end=self.final_t

        comb_ds=xr.concat(ds_grib, 'time')
        # data frame interval in seconds
        self.drv_fld_dt=((comb_ds.time[1].values-comb_ds.time[0].values)/np.timedelta64(1,'s')).tolist()
        # how many time_steps in a data frame
        self.step_per_inpf=self.drv_fld_dt/(int(config['CORE']['time_step'])*60)
        self.U = comb_ds['u'].loc[slice_start:slice_end,:,:]
        self.V = comb_ds['v'].loc[slice_start:slice_end,:,:]
        self.W = comb_ds['w'].loc[slice_start:slice_end,:,:]
        self.xlat = comb_ds.latitude 
        self.xlon = comb_ds.longitude
        self.xz = comb_ds.isobaricInhPa
        
        self.inp_nfrm=len(self.U.time)

        if config['CORE'].getboolean('boundary_check'):
            self.nc_surf_files=[]
                
            self.nc_surf_files.append(input_dir+'/'+fn_timestamp.strftime('%Y%m%d')+'-sl.grib')
            ds_grib = [xr.open_dataset(p, engine='cfgrib', backend_kwargs={'errors': 'ignore'}) for p in self.nc_surf_files]

        
        utils.write_log(print_prefix+'init multi files successfully!')

if __name__ == "__main__":
    pass
