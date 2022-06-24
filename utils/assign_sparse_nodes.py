#/usr/bin/env python3
'''
Date: Jun 15, 2022

Assign tracing lat,lon to nodes in the sparse matrix

N[nodeI,nodeJ] = 1: nodeI--->nodeJ counts 1 times in the trajectory

Zhenning LI
'''
import sys, datetime
from turtle import forward
sys.path.append('../')
import lib
import numpy as np
import pandas as pd
import xarray as xr
from scipy.sparse import lil_matrix, save_npz

def match_nodes(anodes,xlat,xlon):
    '''
    match nodes to lat,lon
    '''
    mlist=[]
    mindis=0.250001
    for ilat, ilon in zip(xlat,xlon):
        dis_lat2d=anodes[:,1]-ilat
        dis_lon2d=anodes[:,2]-ilon
        dis=abs(dis_lat2d)+abs(dis_lon2d)
        if dis.min()<=mindis:
            idx=np.argwhere(dis==dis.min())[0].tolist()[0] # x, y position
            mlist.append(idx)
    return mlist


#------set global attributes below------

# The first [CORE]['start_ymdh'] in config.ini
series_first_ymdh = '2021070100'
# The last [CORE]['start_ymdh'] in config.ini
series_last_ymdh = '2021073100'
# interval hours between each 'start_ymdh'
series_delta_hr = 24
# nodes file
nodes_fn = '../input/input_china_east_lv2_noname.csv'   
# sparse matrix file
sparse_fn = '../output/east_china_sparse_202107.npz'

#------set global attributes above------

if __name__ == "__main__":

    # parse cfg paras
    cfg=lib.cfgparser.read_cfg('../conf/config.ini')
    integration_length = int(cfg['CORE']['integration_length'])
    forward_opt=int(cfg['CORE']['forward_option'])
    out_prefix=cfg['OUTPUT']['out_prefix']

    # read nodes file
    air_in_file=pd.read_csv(
        nodes_fn, names=['idx','lat0', 'lon0', 'h0'], index_col='idx')
    
    # pos of assigned nodes [nodeid, lat,lon]
    lnodes=[]
    for row in air_in_file.itertuples():
        lnodes.append([row.Index, row.lat0, row.lon0])
    nnodes=len(lnodes)
    
    # construct nodes array
    anodes=np.array(lnodes)
    # construct sparse matrix N 
    N=lil_matrix((nnodes,nnodes))

    #------EXCECUTION-------
    # The first initial time
    ini_date=datetime.datetime.strptime(series_first_ymdh,'%Y%m%d%H')

    # The final initial time
    final_date=datetime.datetime.strptime(series_last_ymdh,'%Y%m%d%H')

    # Interval between each initial time
    delta_hr=datetime.timedelta(hours=integration_length*forward_opt)

    curr_date=ini_date
    while curr_date <= final_date:
        end_time=curr_date+delta_hr
        
        curr_str=curr_date.strftime('%Y%m%d%H')
        end_str=end_time.strftime('%Y%m%d%H')
        
        print('>>>>>>>>>>>>>>Assign @ '+curr_str+'-->'+end_str+'<<<<<<<<<<<<<<<<')
        
        # track file
        track_fn = '../output/'+out_prefix+'.I'+curr_str+'0000.E'+end_str+'0000.nc'
        
        # execute
        tck_file=xr.load_dataset(track_fn)
        xlat,xlon=tck_file['xlat'].values,tck_file['xlon'].values
        ntime, nparcels=xlat.shape

        #for iparcel in range(500):
        for iparcel in range(nparcels):
            mlist=match_nodes(anodes,xlat[:,iparcel],xlon[:,iparcel])
            for i in mlist:
                N[i,iparcel]=N[i,iparcel]+1
    
        curr_date=curr_date+datetime.timedelta(hours=series_delta_hr)

    save_npz(sparse_fn,N.tocoo())


