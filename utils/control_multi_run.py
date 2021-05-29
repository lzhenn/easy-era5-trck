#/usr/bin/env python
'''
Date: Oct 28, 2020

auto run for multiple initial times

Zhenning LI

'''
import sys, os
import datetime
sys.path.append('../')
from lib.cfgparser import read_cfg, write_cfg

# The first initial time
ini_date=datetime.datetime.strptime('1998061000','%Y%m%d%H')

# The final initial time
final_date=datetime.datetime.strptime('1998063000','%Y%m%d%H')

# Interval between each initial time
ini_delta=datetime.timedelta(days=1)


era5_prefix='/home/metctm1/array/data/era5/LYN-Meiyu/'
era5_lst=[]
while ini_date <= final_date:

    yyyy=ini_date.strftime('%Y')
    yyyymm=ini_date.strftime('%Y%m')
    yyyymmddhh=ini_date.strftime('%Y%m%d%H')

    era5_fn=ini_date.strftime('%Y%m%d')+'-pl.grib'
    era5_lst.append(era5_prefix+'/'+era5_fn)
    ini_date=ini_date+ini_delta
for era5_fn in era5_lst:
    cfg_hdl=read_cfg('../conf/config.ini')
    cfg_hdl['INPUT']['input_era5']=era5_fn
    print(era5_fn)
    write_cfg(cfg_hdl,'../conf/config.ini')

    # execute run script
    os.system('cd ..; python run.py; cd utils')



