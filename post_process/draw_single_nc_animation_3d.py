#/usr/bin/env python
'''
Date: Nov 16, 2020

Draw air parcel rendering

Zhenning LI

'''
import numpy as np
import xarray as xr
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
from mpl_toolkits.mplot3d import axes3d

# Constants
BIGFONT=18
MIDFONT=14
SMFONT=10

FIG_WIDTH=16
FIG_HEIGHT=7

LON_W=0
LON_E=180
LAT_S=-10
LAT_N=70


traj_file='../output/test.P004703.I20150601000000.E20150527000000.nc'
ps_file='/home/metctm1/array/data/era5/2010-JXW-TP-ERA5/20150527-sl.grib'

#--------------Function Defination----------------

def get_landsea_idx_xy(lsmask, lat2d, lon2d, lat0, lon0, mindis):
    """
        Find the nearest x,y in lat2d and lon2d for lat0 and lon0
    """
    dis_lat2d=lat2d-lat0
    dis_lon2d=lon2d-lon0
    dis=abs(dis_lat2d)+abs(dis_lon2d)
    if dis.min()<=mindis:
        idx=np.argwhere(dis==dis.min())[0].tolist() # x, y position
        return(lsmask[idx[0],idx[1]])
    else:
        return -1

def main():

    xlat = np.arange(LAT_S, LAT_N+0.25, 0.25)
    xlon = np.arange(LON_W, LON_E, 0.25)
    xlon, xlat = np.meshgrid(xlon, xlat)

    # ----------Get NetCDF data------------
    print('Read Traj Rec...')
    ds = xr.open_dataset(traj_file)
    lat_arr=ds['xlat']
    lon_arr=ds['xlon']
    z_arr=ds['xh']
    print('Read terrain pressure file...')
    ds_ps= xr.open_dataset(ps_file,engine='cfgrib')
    ps=ds_ps['sp']

    print('Plot...')
    # Create the figure
    ii=0
    for itime in lat_arr.time[::-1]:

        fig = plt.figure(figsize=[FIG_WIDTH, FIG_HEIGHT],frameon=True)

        ax = fig.add_axes([0.08, 0.05, 0.8, 0.94], projection='3d')
        # Set figure extent
        print(xlat.shape)
        print(xlon.shape)
        ax.scatter( lon_arr.values[0,:], lat_arr[0,:], z_arr[0,:], marker='.', color='green', 
                    s=2, alpha=0.3)
        ax.scatter( lon_arr.sel(time=itime).values, lat_arr.sel(time=itime).values,z_arr.sel(time=itime).values, marker='.', color='blue', 
                s=6, alpha=1.)

        ax.plot_surface(xlon,xlat,ps.sel(latitude=slice(LAT_N, LAT_S), longitude=slice(LON_W, LON_E))/100.0,color="lightgray",
                               rstride=1,cstride=1, alpha=1.,
                                linewidth=0, antialiased=False)
            
        ax.set_facecolor('k')
        ax.set_zlim(1000, 100)
        ax.set_zscale('log')
        ax.set_xlim(LON_W,LON_E)
        ax.set_ylim(LAT_S,LAT_N)
        ax.view_init(elev=53-0.05*ii, azim=-90)
    #    ax.view_init(elev=0, azim=-90)
        ax.grid(False)

        
        plt.axis('off')
     
        plt.title('TP Air Source Tracers %s' % itime.dt.strftime('%Y-%m-%d %H:%M:%S').values,fontsize=MIDFONT)
        plt.savefig("../fig/tp.source.%04d.png" % ii, dpi=120, bbox_inches='tight')
        plt.close('all')
        print('%04d finished.' % ii)
        ii=ii+1
#plt.show()

if __name__ == "__main__":
    main()

 
