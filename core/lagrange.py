#/usr/bin/env python
"""CORE: March the Air Parcel by Lagrangian Approach"""

import configparser
import datetime, math
import numpy as np

print_prefix='core.lagrange>>'

# CONSTANT
R_EARTH=6371000
DIS2LAT=180/(math.pi*R_EARTH)        #Distance to Latitude
CONST={'a':R_EARTH,'dis2lat':DIS2LAT}

def get_closest_idx_lsearch(l1d, tgt_value):
    """
        Find the nearest idx in l1d (linear search)
    """
    dis=abs(tgt_value-l1d)
    return np.argwhere(dis==dis.min())[0].tolist()[0]

def resolve_curr_xyz(airp, lat1d, lon1d, z1d):
    """
    Resolve air parcel location ( h, lat, lon) to (idx_t,idx_z,idx_lat,idx_lon)

    INPUT
    ---------
    """
    airp.ix.append(get_closest_idx_lsearch(lat1d, airp.lat[-1]))
    airp.iy.append(get_closest_idx_lsearch(lon1d, airp.lon[-1]))
    airp.iz.append(get_closest_idx_lsearch(z1d, airp.h[-1]))
    
    
   
   
def lagrange_march(airp, u1d, v1d, w1d, dts):
    """
    March the air parcel (single) in the UVW fields
    """

    dx=u1d*dts
    dlon=dx*180/(CONST['a']*math.sin(math.pi/2-math.radians(airp.lat[-1]))*math.pi)
    
    dy=v1d*dts
    dlat=dy*CONST['dis2lat']
    
    dz=w1d*dts/100 # to hPa

    curr_t = airp.t[-1]+airp.dt

    airp.update(airp.lat[-1]+dlat, airp.lon[-1]+dlon, airp.h[-1]+dz, curr_t)
if __name__ == "__main__":
    pass
