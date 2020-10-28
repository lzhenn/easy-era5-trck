#/usr/bin/env python
'''
Date: Oct 28, 2020

Take TP grid (3000m+) and construct input.csv by all TP grids

Zhenning LI

'''

import xarray as xr
import numpy as np
import csv

if __name__ == "__main__":
    
    init_height=600 # hpa
    threshold_height=3000 # meter
    ds=xr.open_dataset('/disk/v092.yhuangci/lzhenn/elev.0.25-deg.nc')
    
    elev = ds['data']
    lat = ds['lat'] 
    lon = ds['lon']
    elev=elev[0,:,:]
    elev=elev.sel(lon=slice(60,110), lat=slice(45,20))
    print(elev)
    igrid=0
    with open('../input/input.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        for ilat in elev.lat.values:
            for ilon in elev.lon.values:
                if elev.sel(lat=ilat, lon=ilon).values>=threshold_height:
                    spamwriter.writerow([igrid, ilat, ilon, init_height])
                    igrid=igrid+1
        
