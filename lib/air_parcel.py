#/usr/bin/env python
"""Build Air Parcel from Input"""

import configparser
import datetime, csv
import pandas as pd 
print_prefix='lib.air_parcel>>'

class air_parcel:

    '''
    Construct air parcel
    

    Attributes
    -----------

    lat, list
    lon, list
    h, list
    t, datetime list, current time
    t0, datetime
    dt, datetime.timedelta
    idx, integer

    Methods
    -----------


    '''
    
    def __init__(self, idx, lat0, lon0, height0, config, strt_t, forward_flag):
        """ construct air parcel obj """
        
        self.t0=strt_t
        self.dt=datetime.timedelta(minutes=forward_flag*int(config['CORE']['time_step']))

        self.idx = idx
        self.lat=[lat0]
        self.lon=[lon0]
        self.h=[height0]
        self.t=[self.t0]
        
        self.ix=[]
        self.iy=[]
        self.iz=[]

    def update(self, lat_new, lon_new, height_new, time_new):
        """ update air parcel position """
        
        self.lat.append(lat_new)
        self.lon.append(lon_new)
        self.h.append(height_new)
        self.t.append(time_new)
    
    def output(self, cfg):
        """ output air parcel records according to configurations"""
        
        
        out_fn='./output/P%06d.I%s.E%s' % (int(self.idx), self.t0.strftime("%Y%m%d%H%M%S"),self.t[-1].strftime("%Y%m%d%H%M%S"))
        outfrq_per_dt=int(int(cfg['OUTPUT']['out_frq'])/int(cfg['CORE']['time_step']))
        out_data={'lat':self.lat[::outfrq_per_dt], 'lon':self.lon[::outfrq_per_dt], 'h':self.h[::outfrq_per_dt]}
        df=pd.DataFrame(out_data, index=self.t[::outfrq_per_dt])
        df.to_csv(out_fn)

def acc_output(airp_lst, num_acc, cfg, prefix=''):
    """ 
    output air parcel records according to configurations (accumulated)
    """
    outfrq_per_dt=int(int(cfg['OUTPUT']['out_frq'])/int(cfg['CORE']['time_step']))
    
    ipos=0
    acc_t=[]
    acc_lat=[]
    acc_lon=[]
    acc_h=[]
    
    for airp in airp_lst:
        ipos=ipos+1
        acc_t.extend(airp.t[::outfrq_per_dt]) 
        acc_lat.extend(airp.lat[::outfrq_per_dt]) 
        acc_lon.extend(airp.lon[::outfrq_per_dt]) 
        acc_h.extend(airp.h[::outfrq_per_dt]) 
        if ipos % num_acc ==0:
            out_fn='./output/%sP%06d.I%s.E%s' % (prefix, int(airp.idx), airp.t0.strftime("%Y%m%d%H%M%S"), airp.t[-1].strftime("%Y%m%d%H%M%S"))
            with open(out_fn, 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',')
                for row in zip(acc_t, acc_lat, acc_lon, acc_h):
                    spamwriter.writerow(row)
            acc_t=[]
            acc_lat=[]
            acc_lon=[]
            acc_h=[]

    out_fn='./output/P%06d.I%s.E%s' % (int(airp_lst[-1].idx), airp_lst[-1].t0.strftime("%Y%m%d%H%M%S"), airp_lst[-1].t[-1].strftime("%Y%m%d%H%M%S"))
    with open(out_fn, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        for row in zip(acc_t, acc_lat, acc_lon, acc_h):
            spamwriter.writerow(row)


    
if __name__ == "__main__":
    pass
