#/usr/bin/env python
'''
Date: Sep 2, 2020


Zhenning LI

'''

from netCDF4 import Dataset
from wrf import getvar, ALL_TIMES
import datetime
import numpy as np
import csv
import configparser
import sys
sys.path.append('../')
from lib.cfgparser import read_cfg

def get_closest_idx_xy(lat2d, lon2d, lat0, lon0, dismin):
    """
        Find the nearest x,y in lat2d and lon2d for lat0 and lon0
    """
    dis_lat2d=lat2d-lat0
    dis_lon2d=lon2d-lon0
    dis=abs(dis_lat2d)+abs(dis_lon2d)
    if dis.min()<=dismin:
        idx=np.argwhere(dis==dis.min())[0].tolist() # x, y position
        return idx
    else:
        return 0

if __name__ == "__main__":
    
    out_num_acc=5000
    mindis=0.3
    print('Read Air Parcel Input...')
    with open('../input/input.csv') as f:
        airp_count = sum(1 for row in f) 
    
    print('Read Config...')
    config=read_cfg('../conf/config.ini')
    
    strt_time=datetime.datetime.strptime(config['INPUT']['input_wrf'][-19:],'%Y-%m-%d_%H:%M:%S')
    final_time=strt_time+datetime.timedelta(hours=int(config['CORE']['integration_length']))
    
    #number of nc files 
    nfiles=int(config['CORE']['integration_length'])//(int(config['INPUT']['input_file_dt'])//60)
    # add 1 to outlen (init---end)
    airp_outlen=int(int(config['CORE']['integration_length'])/(int(config['OUTPUT']['out_frq'])/60))+1
    fname_prefix=config['INPUT']['input_wrf'][:-19]
    
    # -----------generate traj file name lists------------
    trj_fn_lst=[]
    for ii in range(airp_count//out_num_acc):
        trj_fn_lst.append('../output/P%06d.I%s.E%s' % ((ii+1)*out_num_acc-1, strt_time.strftime("%Y%m%d%H%M%S"), final_time.strftime("%Y%m%d%H%M%S")))
    if airp_count % out_num_acc >0:
        trj_fn_lst.append('../output/P%06d.I%s.E%s' % (airp_count-1, strt_time.strftime("%Y%m%d%H%M%S"), final_time.strftime("%Y%m%d%H%M%S")))

    # ----------read template wrf input---------
    ncfiles=[]
    for ii in range(0,nfiles+1):
        fn_timestamp=strt_time+datetime.timedelta(hours=ii)
        ncfiles.append(Dataset(fname_prefix+fn_timestamp.strftime('%Y-%m-%d_%H:%M:%S')))

    ncfile=Dataset(config['INPUT']['input_wrf'])
    
   
    restime = getvar(ncfiles, 'LANDMASK',timeidx=ALL_TIMES, method="cat")
    xlat = getvar(ncfiles, 'XLAT')
    xlon = getvar(ncfiles, 'XLONG')
    
    xlat_nparry=xlat.values
    xlon_nparry=xlon.values

    restime.name='OcnResTime'
    restime.values.fill(0) # reset to zero
    restime_nparray=restime.values
    
    outnc_fn='../outnc/OceanAccup.I%s.E%s.nc' % (strt_time.strftime("%Y%m%d%H%M%S"), final_time.strftime("%Y%m%d%H%M%S"))
    restime.values=restime_nparray
    restime.attrs['projection']=''
    restime.to_netcdf(outnc_fn)
    
    # ----------read traj output files---------
    for trj_fn in trj_fn_lst:
        print(trj_fn)
        with open(trj_fn, 'r', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            lcount=0
            for row in spamreader:
                # 1---lat0, 2---lon0
                lat0=float(row[1])
                lon0=float(row[2])
                itime=lcount % airp_outlen 
                lcount=lcount+1
                idx=get_closest_idx_xy(xlat_nparry, xlon_nparry, lat0, lon0, mindis)
                if (idx != 0):
                    restime_nparray[itime, idx[0], idx[1]] = 1     
    
    # ----------output-----------
    outnc_fn='../outnc/OceanAccup.I%s.E%s.nc' % (strt_time.strftime("%Y%m%d%H%M%S"), final_time.strftime("%Y%m%d%H%M%S"))
    restime.values=restime_nparray
    restime.attrs['projection']=''
    restime.to_netcdf(outnc_fn)


