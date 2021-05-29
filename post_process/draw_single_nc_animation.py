#/usr/bin/env python
'''
Date: Nov 16, 2020

Draw air parcel rendering

Zhenning LI

'''
import numpy as np
import xarray as xr
import datetime, csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import shapely.geometry as sgeom
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from copy import copy

import sys
sys.path.append('../')
from lib.cfgparser import read_cfg



# Constants
BIGFONT=18
MIDFONT=14
SMFONT=10

FIG_WIDTH=10
FIG_HEIGHT=9

LON_W=40
LON_E=120
LAT_S=-10
LAT_N=60

prefix='test'
traj_file='../output/test.I20150531000000.E20150530000000.nc'


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


def find_side(ls, side):
    """
 Given a shapely LineString which is assumed to be rectangular, return the
 line corresponding to a given side of the rectangle.
 """
    minx, miny, maxx, maxy = ls.bounds
    points = {'left': [(minx, miny), (minx, maxy)],
              'right': [(maxx, miny), (maxx, maxy)],
              'bottom': [(minx, miny), (maxx, miny)],
              'top': [(minx, maxy), (maxx, maxy)],}
    return sgeom.LineString(points[side])
def lambert_xticks(ax, ticks):
    """Draw ticks on the bottom x-axis of a Lambert Conformal projection."""
    te = lambda xy: xy[0]
    lc = lambda t, n, b: np.vstack((np.zeros(n) + t, np.linspace(b[2], b[3], n))).T
    xticks, xticklabels = _lambert_ticks(ax, ticks, 'bottom', lc, te)
    ax.xaxis.tick_bottom()
    ax.set_xticks(xticks)
    ax.set_xticklabels([ax.xaxis.get_major_formatter()(xtick) for xtick in xticklabels], fontsize=MIDFONT)
def lambert_yticks(ax, ticks):
    """Draw ricks on the left y-axis of a Lamber Conformal projection."""
    te = lambda xy: xy[1]
    lc = lambda t, n, b: np.vstack((np.linspace(b[0], b[1], n), np.zeros(n) + t)).T
    yticks, yticklabels = _lambert_ticks(ax, ticks, 'left', lc, te)
    ax.yaxis.tick_left()
    ax.set_yticks(yticks)
    ax.set_yticklabels([ax.yaxis.get_major_formatter()(ytick) for ytick in yticklabels], fontsize=MIDFONT)
def _lambert_ticks(ax, ticks, tick_location, line_constructor, tick_extractor):
    """Get the tick locations and labels for an axis of a Lambert Conformal projection."""
    outline_patch = sgeom.LineString(ax.outline_patch.get_path().vertices.tolist())
    axis = find_side(outline_patch, tick_location)
    n_steps = 30
    extent = ax.get_extent(ccrs.PlateCarree())
    _ticks = []
    for t in ticks:
        xy = line_constructor(t, n_steps, extent)
        proj_xyz = ax.projection.transform_points(ccrs.Geodetic(), xy[:, 0], xy[:, 1])
        xyt = proj_xyz[..., :2]
        ls = sgeom.LineString(xyt.tolist())
        locs = axis.intersection(ls)
        if not locs:
            tick = [None]
        else:
            tick = tick_extractor(locs.xy)
        _ticks.append(tick[0])
    # Remove ticks that aren't visible: 
    ticklabels = copy(ticks)
    while True:
        try:
            index = _ticks.index(None)
        except ValueError:
            break
        _ticks.pop(index)
        ticklabels.pop(index)
    return _ticks, ticklabels

def main():

    # ----------Get NetCDF data------------
    print('Read Traj Rec...')
    ds = xr.open_dataset(traj_file)
    print(ds)
    lat_arr=ds['xlat']
    lon_arr=ds['xlon']


    print('Plot...')
    # Create the figure
    ii=0
    for itime in lat_arr.time[::-1]:
        # Get the map projection information
        #proj = ccrs.LambertConformal(central_longitude=85, central_latitude=90,
        #                            false_easting=400000, false_northing=400000)#,standard_parallels=(46, 49))
 
        proj = ccrs.PlateCarree(central_longitude=85)

        fig = plt.figure(figsize=[FIG_WIDTH, FIG_HEIGHT],frameon=True)


        ax = fig.add_axes([0.08, 0.05, 0.8, 0.94], projection=proj)
        # Set figure extent
        ax.set_extent([LON_W, LON_E, LAT_S, LAT_N],crs=ccrs.PlateCarree())


        # Download and add the states and coastlines
        ax.coastlines('50m', linewidth=0.8)

        # Add ocean, land, rivers and lakes
        ax.add_feature(cfeature.OCEAN.with_scale('50m'))
        ax.add_feature(cfeature.LAND.with_scale('50m'))
        ax.add_feature(cfeature.LAKES.with_scale('50m'))

        # *must* call draw in order to get the axis boundary used to add ticks:
        fig.canvas.draw()
        # Define gridline locations and draw the lines using cartopy's built-in gridliner:
        # xticks = np.arange(80,130,10)
        # yticks = np.arange(15,55,5)
        xticks = np.arange(LON_W,LON_E,20).tolist() 
        yticks =  np.arange(LAT_S,LAT_N,15).tolist() 
        #ax.gridlines(xlocs=xticks, ylocs=yticks,zorder=1,linestyle='--',lw=0.5,color='gray')

        # Label the end-points of the gridlines using the custom tick makers:
        ax.xaxis.set_major_formatter(LONGITUDE_FORMATTER) 
        ax.yaxis.set_major_formatter(LATITUDE_FORMATTER)
        lambert_xticks(ax, xticks)
        lambert_yticks(ax, yticks)



        # Set the map bounds
        #ax.set_xlim(cartopy_xlim(lsmask))
        #ax.set_ylim(cartopy_ylim(lsmask))

        ax.scatter( lon_arr.values[0,:], lat_arr[0,:],marker='.', color='darkred', 
                    s=2, zorder=1, alpha=0.5, transform=ccrs.PlateCarree())
        ax.scatter( lon_arr.sel(time=itime).values, lat_arr.sel(time=itime).values,marker='.', color='blue', 
                s=6, zorder=2, alpha=0.5, transform=ccrs.PlateCarree())
     
        print('%04d finished.' % ii)
        plt.title('Air Source Tracers %s' % itime.dt.strftime('%Y-%m-%d %H:%M:%S').values,fontsize=MIDFONT)
        plt.savefig('../fig/'+prefix+'.%04d.png' % ii, dpi=120, bbox_inches='tight')
        plt.close('all')
        ii=ii+1
#plt.show()

if __name__ == "__main__":
    main()

 
