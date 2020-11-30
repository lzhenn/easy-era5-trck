#/usr/bin/env python
'''
Date: Sep 5, 2020

Draw bitmaps rendering

Zhenning LI

'''

import xarray as xr
import datetime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

if __name__ == "__main__":
    
    ds=xr.open_dataset("../outnc/OceanAccup.I20161031120000.E20161103120000.nc")
    
    restime = ds['OcnResTime']
    fig, ax=plt.subplots()
    fig.subplots_adjust(left=0.08, bottom=0.18, right=0.99, top=0.92, wspace=None, hspace=None) 

    for ii in range(0,len(restime.datetime)):
        ax.imshow(restime.values[ii,::-1,:], cmap='gray')
        plt.title( 'Ocean-sourced Mass Points @%s' % restime.datetime[ii].dt.strftime('%Y-%m-%d %H:%M:%S').values)
        fig.savefig('../fig/bitmap.%04d.png' % ii)

