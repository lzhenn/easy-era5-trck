#/usr/bin/env python
'''
Date: Sep 5, 2020

Draw partical rendering with map

Zhenning LI

'''
from netCDF4 import Dataset
import numpy as np
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

from wrf import (getvar, interplevel, to_np, latlon_coords, get_cartopy,
                 cartopy_xlim, cartopy_ylim, ALL_TIMES)
import sys
sys.path.append('../')
from lib.cfgparser import read_cfg



# Constants
BIGFONT=18
MIDFONT=14
SMFONT=10



#--------------Function Defination----------------


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

def mct_xticks(ax, ticks):
    """Draw ticks on the bottom x-axis of a Lambert Conformal projection."""
    te = lambda xy: xy[0]
    lc = lambda t, n, b: np.vstack((np.zeros(n) + t, np.linspace(b[2], b[3], n))).T
    xticks, xticklabels = _mct_ticks(ax, ticks, 'bottom', lc, te)
    ax.xaxis.tick_bottom()
    ax.set_xticks(xticks)
    ax.set_xticklabels([ax.xaxis.get_major_formatter()(xtick) for xtick in xticklabels], fontsize=MIDFONT)
def mct_yticks(ax, ticks):
    """Draw ricks on the left y-axis of a Lamber Conformal projection."""
    te = lambda xy: xy[1]
    lc = lambda t, n, b: np.vstack((np.linspace(b[0], b[1], n), np.zeros(n) + t)).T
    yticks, yticklabels = _mct_ticks(ax, ticks, 'left', lc, te)
    ax.yaxis.tick_left()
    ax.set_yticks(yticks)
    ax.set_yticklabels([ax.yaxis.get_major_formatter()(ytick) for ytick in yticklabels], fontsize=MIDFONT)
def _mct_ticks(ax, ticks, tick_location, line_constructor, tick_extractor):
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



# Read Trajs
out_num_acc=5000

# get total points number
print('Read Air Parcel Input...')
with open('../input/input_GBA_d01.csv') as f:
    airp_count = sum(1 for row in f) 

print('Read Config...')
config=read_cfg('../conf/config_gba_d01.ini')



# ----------Get NetCDF data------------
print('Read NC...')
ncfile = Dataset("/disk/v092.yhuangci/lzhenn/1911-COAWST/WRFONLY/wrfout_d01")

# Extract the pressure, geopotential height, and wind variables
slp = getvar(ncfile, 'slp', timeidx=ALL_TIMES, method ='cat')

# Get the lat/lon coordinates
lats, lons = latlon_coords(slp)


print('Read Traj Rec...')
# -----------generate traj file name lists------------
airp_outlen=int(int(config['CORE']['integration_length'])/(int(config['OUTPUT']['out_frq'])/60))+1
strt_time=datetime.datetime.utcfromtimestamp(slp[0,:,:].Time.values.tolist()/1e9)
final_time=strt_time+datetime.timedelta(hours=int(config['CORE']['integration_length']))

trj_fn_lst=[]
for ii in range(airp_count//out_num_acc):
    trj_fn_lst.append('../output/gba.d01.P%06d.I%s.E%s' % ((ii+1)*out_num_acc-1, strt_time.strftime("%Y%m%d%H%M%S"), final_time.strftime("%Y%m%d%H%M%S")))
if airp_count % out_num_acc >0:
    trj_fn_lst.append('../output/gba.d01.P%06d.I%s.E%s' % (airp_count-1, strt_time.strftime("%Y%m%d%H%M%S"), final_time.strftime("%Y%m%d%H%M%S")))

# ----------read traj output files---------
lat_arr=np.zeros((airp_count, airp_outlen))
lon_arr=np.zeros((airp_count, airp_outlen))
h_arr=np.zeros((airp_count, airp_outlen))

lcount=0
for trj_fn in trj_fn_lst:
    print(trj_fn)
    with open(trj_fn, 'r', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            #0---time 1---lat0, 2---lon0
            lat0=float(row[1])
            lon0=float(row[2])
            h0=float(row[3])
            itime=int(lcount % airp_outlen )
            icount=int(lcount // airp_outlen )
            lat_arr[icount, itime]=lat0
            lon_arr[icount, itime]=lon0
            h_arr[icount, itime]=h0
            lcount=lcount+1
    
print('Plot...')
# Create the figure
for ii in range(0, airp_outlen):
    # Get the map projection information
    fig = plt.figure(figsize=(11,8), frameon=True)
    proj = get_cartopy(slp)


    ax = fig.add_axes([0.08, 0.05, 0.8, 0.94], projection=proj)

    # Download and add the states and coastlines
    ax.coastlines('50m', linewidth=0.8)

    # Add the SLP contours
    levels = np.arange(950., 1000., 5.)
    contours = plt.contour(to_np(lons), to_np(lats), to_np(slp[ii,:,:]),
                           levels=levels, colors="blue",zorder=10,
                           transform=ccrs.PlateCarree())
    #plt.clabel(contours, inline=1, fontsize=10, fmt="%i")

    # Add ocean, land, rivers and lakes
    ax.add_feature(cfeature.OCEAN.with_scale('50m'))
    ax.add_feature(cfeature.LAND.with_scale('50m'))
    ax.add_feature(cfeature.LAKES.with_scale('50m'))

    # *must* call draw in order to get the axis boundary used to add ticks:
    fig.canvas.draw()
    # Define gridline locations and draw the lines using cartopy's built-in gridliner:
    # xticks = np.arange(80,130,10)
    # yticks = np.arange(15,55,5)
    xticks = np.arange(100,135,5).tolist() 
    yticks =  np.arange(5,40,5).tolist() 
    #ax.gridlines(xlocs=xticks, ylocs=yticks,zorder=1,linestyle='--',lw=0.5,color='gray')

    # Label the end-points of the gridlines using the custom tick makers:
    ax.xaxis.set_major_formatter(LONGITUDE_FORMATTER) 
    ax.yaxis.set_major_formatter(LATITUDE_FORMATTER)
    mct_xticks(ax, xticks)
    mct_yticks(ax, yticks)



    # Set the map bounds
    ax.set_xlim(cartopy_xlim(slp))
    ax.set_ylim(cartopy_ylim(slp))




    ax.scatter( lon_arr[:,ii], lat_arr[:,ii],marker='.', c=h_arr[:,ii], cmap='rainbow',vmin=0,vmax=10000, 
                s=6, zorder=1, alpha=0.8, transform=ccrs.Geodetic(), label='Mass Points')
     
    print('%04d finished.' % ii)
    plt.title('Universial Mass Points and SLP @%s' % slp[ii,:,:].Time.dt.strftime('%Y-%m-%d %H:%M:%S').values,fontsize=MIDFONT)
    plt.savefig("../fig/mangkhut.d01.%04d.png" % ii, dpi=80, bbox_inches='tight')
    plt.close('all')

#plt.show()


