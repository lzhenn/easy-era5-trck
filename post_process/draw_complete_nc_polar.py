#/usr/bin/env python
'''
Date: Nov 16, 2020

Draw air parcel rendering

Zhenning LI

'''
import numpy as np
import pandas as pd
import xarray as xr
import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


import sys
sys.path.append('../')
import lib
import lib.utils as utils




# Constants
BIGFONT=18
MIDFONT=14
SMFONT=10

FIG_WIDTH=10
FIG_HEIGHT=10

LON_W=0
LON_E=359
LAT_S=-90
LAT_N=-40

strt_time_str='2015122200'
end_time_str='2016012100'

# The first initial time
ini_date=datetime.datetime.strptime(strt_time_str,'%Y%m%d%H')

# The final initial time
final_date=datetime.datetime.strptime(end_time_str,'%Y%m%d%H')

# Interval between each initial time
ini_delta=datetime.timedelta(days=1)


#--------------Function Defination----------------

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

    cfg_hdl=lib.cfgparser.read_cfg('../conf/config.ini')
    painter=painter_class(cfg_hdl, ini_date, final_date, ini_delta)
    
    # Create the figure
    proj =ccrs.SouthPolarStereo()
    
    for ii, itime in enumerate(painter.glb_clock):
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
        # Set the map bounds
        #ax.set_xlim(cartopy_xlim(lsmask))
        #ax.set_ylim(cartopy_ylim(lsmask))

        # Compute a circle in axes coordinates, which we can use as a boundary
        # for the map. We can pan/zoom as much as we like - the boundary will be
        # permanently circular.
        theta = np.linspace(0, 2*np.pi, 100)
        center, radius = [0.5, 0.5], 0.5
        verts = np.vstack([np.sin(theta), np.cos(theta)]).T
        circle = mpath.Path(verts * radius + center)

        ax.set_boundary(circle, transform=ax.transAxes)


        # aim points
        ax.scatter( painter.aim_lon_set, painter.aim_lat_set, marker='.', color='darkred', 
                    s=2, zorder=1, alpha=0.5, transform=ccrs.PlateCarree())
        
        ax.scatter( painter.firework_lon, painter.firework_lat, marker='.', color='blue', 
                s=6, zorder=2, alpha=0.5, transform=ccrs.PlateCarree())
     
        print('%04d finished.' % ii)
        plt.title('Air Source Tracers %s' % itime.strftime('%Y-%m-%d %H:%M:%S'),fontsize=MIDFONT)
        plt.savefig("../fig/SP_Jan16.%04d.png" % ii, dpi=100)
        plt.close('all')

if __name__ == "__main__":
    main()

 
