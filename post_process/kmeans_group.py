#!/usr/bin/env python
'''
Date: Mar 5, 2022

Do K-means clustering on the output data

Zhenning LI

'''
from netCDF4 import Dataset
import xarray as xr
from ..lib.cfgparser import read_cfg

# Constants
BIGFONT=18
MIDFONT=14
SMFONT=10

traj_file='../output/SP_Jan16.I20151227000000.E20151222000000.nc'

#--------------Function Defination----------------

# get total points number

print('Read Config...')
config=read_cfg('../conf/config.ini')

# ----------Get NetCDF data------------
print('Read Traj Rec...')
ds = xr.open_dataset(traj_file)
print(ds)
lat_arr=ds['xlat']
lon_arr=ds['xlon']

#plt.show()

  
