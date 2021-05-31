#/usr/bin/env python
'''
Date: Nov 16, 2020

Draw air parcel rendering

Zhenning LI

'''
import numpy as np
import pandas as pd
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

LON_W=10
LON_E=350
LAT_S=-90
LAT_N=-10

strt_time_str='2015122500'
end_time_str='2016012100'

# The first initial time
ini_date=datetime.datetime.strptime(strt_time_str,'%Y%m%d%H')

# The final initial time
final_date=datetime.datetime.strptime(end_time_str,'%Y%m%d%H')

# Interval between each initial time
ini_delta=datetime.timedelta(days=1)


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

class painter_class:

    '''
    Construct a painting controller to dispatch the painting

    Attributes
    ------------
    
    glb_clock, global clock, datetime date_range list
    infile_lst,  input file list, string list
    pulse_clock, infile pulse clock, datetime date_range list
    forward_option, int

    curr_time, datetime
    
    airp_lat_set, list of painted air parcel lat tracks, 
        [0..n] for n+1 individual files structure:[ifile][itime, idx]
    airp_lon_set, list of painted air parcel lon tracks,
        [0..n] for n+1 individual files structure:[ifile][itime, idx]

    firework_lat, list of current parcels lat
    firework_lon, list of current parcels lon

    Methods
    ------------
    advance, advance the painter to the next painting

    '''
    def __init__(self, config, ini_date, final_date, ini_delta):
        self.int_length=int(config['CORE']['integration_length'])
        self.out_frq=int(config['OUTPUT']['out_frq'])/60 # to hours
        self.out_prefix=config['OUTPUT']['out_prefix']
        self.forward_option=int(config['CORE']['forward_option'])

        self.airp_lat_set=[]
        self.airp_lon_set=[]
        ''' 
        if self.forward_option > 0:
            painting_ini_date=ini_date
        else:
            painting_ini_date=ini_date+datetime.timedelta(hours=self.forward_option*self.int_length)
        '''     
        self.glb_clock=pd.date_range(ini_date, final_date, freq=str(self.out_frq)+'H')
        self.pulse_clock=pd.date_range(ini_date, final_date, freq=ini_delta)

    def stoke(self):
        ''' Add fuel to the fire work!'''
        print('!!!STOKE: Read Traj Rec...')
        later_date_str=(self.curr_time+datetime.timedelta(hours=self.int_length)).strftime('%Y%m%d%H%M%S')
        earlier_date_str=self.curr_time.strftime('%Y%m%d%H%M%S')

        if self.forward_option >0:
            fn='../output/%s.I%s.E%s.nc' % (self.out_prefix, earlier_date_str, later_date_str)
        else:
            fn='../output/%s.I%s.E%s.nc' % (self.out_prefix, later_date_str, earlier_date_str)
        ds = xr.open_dataset(fn)
        self.airp_lat_set.append(ds['xlat'][::-1,:])
        self.airp_lon_set.append(ds['xlon'][::-1,:])

        self.aim_lat_set=ds['xlat'][0,:].values
        self.aim_lon_set=ds['xlon'][0,:].values

    def collect_cinders(self):
        ''' Remove cinder from the fire work!'''
        print('!!!Cinder Collect...')
        self.airp_lat_set=[airpset for airpset in self.airp_lat_set if airpset.time[-1] != self.curr_time]
        self.airp_lon_set=[airpset for airpset in self.airp_lon_set if airpset.time[-1] != self.curr_time]

    def cast_firework(self):
        ''' Select air parcels for the current firework!'''
        
        self.firework_lat=[]
        self.firework_lon=[]
        for elem_lat_set, elem_lon_set in zip(self.airp_lat_set, self.airp_lon_set):
            self.firework_lat.extend(elem_lat_set.sel(time=self.curr_time).values)
            self.firework_lon.extend(elem_lon_set.sel(time=self.curr_time).values)

def main():


    cfg_hdl=read_cfg('../conf/config.ini')
    painter=painter_class(cfg_hdl, ini_date, final_date, ini_delta)
    
    # Create the figure
    proj = ccrs.PlateCarree(central_longitude=85)
    
    ii = 0 
    for itime in painter.glb_clock:
        print(itime)            
        painter.curr_time=itime
        
        if itime in painter.pulse_clock: 
            if (itime+datetime.timedelta(hours=painter.int_length)) <= final_date: 
                # add fuel to the stove
                painter.stoke() 
            
            if (itime-datetime.timedelta(hours=painter.int_length)) >= ini_date: 
                # collect cinders
                painter.collect_cinders()   
        
   
        # cast current firework with current air parcels
        painter.cast_firework()
  
  
        print('Painting...')
        # Get the map projection information
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

        # aim points
        ax.scatter( painter.aim_lon_set, painter.aim_lat_set, marker='.', color='darkred', 
                    s=2, zorder=1, alpha=0.5, transform=ccrs.PlateCarree())
        
        ax.scatter( painter.firework_lon, painter.firework_lat, marker='.', color='blue', 
                s=6, zorder=2, alpha=0.5, transform=ccrs.PlateCarree())
     
        print('%04d finished.' % ii)
        plt.title('Air Source Tracers %s' % itime.strftime('%Y-%m-%d %H:%M:%S'),fontsize=MIDFONT)
        plt.savefig("../fig/SP_Jan16.%04d.png" % ii, dpi=90, bbox_inches='tight')
        plt.close('all')
        ii=ii+1
#plt.show()

if __name__ == "__main__":
    main()

 
