#/usr/bin/env python
'''
Date: Nov 16, 2020

Draw air parcel rendering

Zhenning LI

'''
import numpy as np
import xarray as xr
import matplotlib
matplotlib.use('Agg')
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER

# Constants
BIGFONT=18
MIDFONT=14
SMFONT=10

FIG_WIDTH=8
FIG_HEIGHT=8

LON_W=0
LON_E=359
LAT_S=-90
LAT_N=-40

prefix='testcase'
traj_file='../output/testcase.I20050103000000.E20041229000000.nc'


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

    # ----------Get NetCDF data------------
    print('Read Traj Rec...')
    ds = xr.open_dataset(traj_file)
    print(ds)
    lat_arr=ds['xlat']
    lon_arr=ds['xlon']


    print('Plot...')
    # Create the figure
    for ii, itime in enumerate(lat_arr.time[::-1]):
        # Get the map projection information
        #proj = ccrs.LambertConformal(central_longitude=85, central_latitude=90,
        #                            false_easting=400000, false_northing=400000)#,standard_parallels=(46, 49))
 
        proj =ccrs.SouthPolarStereo()

        fig = plt.figure(figsize=[FIG_WIDTH, FIG_HEIGHT])


        ax = fig.add_axes([0.08, 0.05, 0.8, 0.94], projection=proj)
        # Set figure extent
        ax.set_extent([LON_W, LON_E, LAT_S, LAT_N],crs=ccrs.PlateCarree())


        # Download and add the states and coastlines
        ax.coastlines('50m', linewidth=0.8)

        # Add ocean, land, rivers and lakes
        ax.add_feature(cfeature.OCEAN.with_scale('50m'))
        ax.add_feature(cfeature.LAND.with_scale('50m'))
        #ax.add_feature(cfeature.LAKES.with_scale('50m'))
        
        # *must* call draw in order to get the axis boundary used to add ticks:
        fig.canvas.draw()
        # Define gridline locations and draw the lines using cartopy's built-in gridline:
        # xticks = np.arange(80,130,10)
        # yticks = np.arange(15,55,5)
        xticks = np.arange(LON_W,LON_E,20).tolist() 
        yticks =  np.arange(LAT_S,LAT_N,15).tolist() 
        #ax.gridlines(xlocs=xticks, ylocs=yticks,zorder=1,linestyle='--',lw=0.5,color='gray')

        # Label the end-points of the gridlines using the custom tick makers:
        ax.xaxis.set_major_formatter(LONGITUDE_FORMATTER) 
        ax.yaxis.set_major_formatter(LATITUDE_FORMATTER)

        # Compute a circle in axes coordinates, which we can use as a boundary
        # for the map. We can pan/zoom as much as we like - the boundary will be
        # permanently circular.
        theta = np.linspace(0, 2*np.pi, 100)
        center, radius = [0.5, 0.5], 0.5
        verts = np.vstack([np.sin(theta), np.cos(theta)]).T
        circle = mpath.Path(verts * radius + center)

        ax.set_boundary(circle, transform=ax.transAxes)



        # Set the map bounds
        #ax.set_xlim(cartopy_xlim(lsmask))
        #ax.set_ylim(cartopy_ylim(lsmask))

        ax.scatter( lon_arr.values[0,:], lat_arr[0,:],marker='.', color='darkred', 
                    s=2, zorder=1, alpha=0.5, transform=ccrs.PlateCarree())
        ax.scatter( lon_arr.sel(time=itime).values, lat_arr.sel(time=itime).values,marker='.', color='blue', 
                s=6, zorder=2, alpha=0.5, transform=ccrs.PlateCarree())
 


        print('%04d finished.' % ii)
        plt.title('Air Source Tracers %s' % itime.dt.strftime('%Y-%m-%d %H:%M:%S').values,fontsize=MIDFONT)
        plt.savefig('../fig/'+prefix+'.%04d.png' % ii, dpi=100)
        plt.close('all')

if __name__ == "__main__":
    main()

 
