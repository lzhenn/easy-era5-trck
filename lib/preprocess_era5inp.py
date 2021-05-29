#/usr/bin/env python
"""Preprocessing the ERA5 input file"""

import configparser
import datetime
import numpy as np
import xarray as xr
import gc
import os

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
        
        if config['INPUT'].getboolean('input_multi_files'):
            print(print_prefix+'init multi files...')
            
            input_dir, init_fn=os.path.split(config['INPUT']['input_era5'])

            

            self.forward=int(config['CORE']['forward_option'])
            self.strt_t=datetime.datetime.strptime(init_fn[:8],'%Y%m%d')
            self.final_t=self.strt_t+datetime.timedelta(hours=self.forward*int(config['CORE']['integration_length']))
            nfiles=int(config['CORE']['integration_length'])//(int(config['INPUT']['input_file_dt'])//60)+1
            
            self.nc_pres_files=[]
            
            for ii in range(0,nfiles):
                fn_timestamp=self.strt_t+datetime.timedelta(days=ii*self.forward)
                print(fn_timestamp)
                self.nc_pres_files.append(input_dir+'/'+fn_timestamp.strftime('%Y%m%d')+'-pl.grib')
                ds_grib = [xr.open_dataset(p, engine='cfgrib', backend_kwargs={'errors': 'ignore'}) for p in self.nc_pres_files]
               
            comb_ds=xr.concat(ds_grib, 'time')
            #from ns to s, time interval in driven file
            self.drv_fld_dt=((comb_ds.time[1].values-comb_ds.time[0].values)/np.timedelta64(1,'s')).tolist()
            #print(comb_ds.time.values.tolist().index(np.datetime64(self.strt_t.strftime('%Y-%m-%dT00:00:00'))))
            #print(np.where(comb_ds.time.values==np.datetime64(self.strt_t.strftime('%Y-%m-%dT00:00:00'))))
            
            self.U = comb_ds['u'].loc[self.strt_t:self.final_t,:,:]
            self.V = comb_ds['v'].loc[self.strt_t:self.final_t,:,:]
            self.W = comb_ds['w'].loc[self.strt_t:self.final_t,:,:]
            self.xlat = comb_ds.latitude 
            self.xlon = comb_ds.longitude
            self.xz = comb_ds.isobaricInhPa
            if config['CORE'].getboolean('boundary_check'):
                self.nc_surf_files=[]
                    
                self.nc_surf_files.append(input_dir+'/'+fn_timestamp.strftime('%Y%m%d')+'-sl.grib')
                ds_grib = [xr.open_dataset(p, engine='cfgrib', backend_kwargs={'errors': 'ignore'}) for p in self.nc_surf_files]

            
            print(print_prefix+'init multi files successfully!')
        else:
            print(print_prefix+'init from single input file not supported now...')

if __name__ == "__main__":
    pass
