#/usr/bin/env python
'''
Date: Sep 2, 2020

Take landsea mask from wrf output and construct input.csv by all ocean grid

Zhenning LI

'''

from netCDF4 import Dataset
from wrf import getvar
import numpy as np
import csv

if __name__ == "__main__":
    
    init_height=100
    ncfile=Dataset("/disk/v092.yhuangci/lzhenn/1911-COAWST/WRFONLY/wrfout_d01")
    
    xlat = getvar(ncfile, 'XLAT')
    xlon = getvar(ncfile, 'XLONG')

    xlat1d=xlat.values.flatten()
    xlon1d=xlon.values.flatten()
    igrid=0
    with open('../input/input_GBA_d01.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        for ilat, ilon in zip(xlat1d, xlon1d):
            spamwriter.writerow([igrid, ilat, ilon, init_height])
            igrid=igrid+1
        
