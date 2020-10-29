#/usr/bin/env python3
'''
Date: Oct 28, 2020

Main script to drive the easy-era5-trac model

Zhenning LI
'''

import numpy as np
import pandas as pd
import  lib.preprocess_era5inp, lib.air_parcel
from lib.cfgparser import read_cfg
import core.lagrange
import os, time
from multiprocessing import Pool, sharedctypes

def lag_run_seriel(itsk, airp_lst, u4d, v4d, w4d, z4d, lat1d, lon1d, dts, inpf_per_dt, final_t):
    """
    Lagrangian run function for seriel
    """
    
    start = time.time()
    while(airp_lst[0].t[-1] < final_t): # not reach the final step

        # ***Elemental Operation of Lagrangian Model***
        # update global idt
        idt=int(round((len(airp_lst[0].t)-1)/inpf_per_dt,0))         
        curr_t=airp_lst[0].t[-1].strftime('%Y-%m-%d %H:%M:%S')
    
        print('TASK[%02d]: Lagrangian Run at %s' % ( itsk, curr_t))

        for airp in airp_lst:
            # resolve ix iy iz for the last (T+0) move
            core.lagrange.resolve_curr_xyz(airp, lat1d, lon1d, z4d[idt,:,:,:]) 
            
            idz=airp.iz[-1]
            idx=airp.ix[-1]
            idy=airp.iy[-1]
            # march all parcels (T+1)
            core.lagrange.lagrange_march(airp, u4d[idt,idz,idx,idy], v4d[idt,idz,idx,idy], w4d[idt, idz,idx,idy], dts)

    end = time.time()
    print('TASK[%02d] END: Lagrangian Run at %s, used %0.3f seconds' % (itsk, curr_t, (end - start)))

def lag_run_mtsk(itsk, airp_lst, dts, inpf_per_dt, forward_flag, strt_t, final_t):
    """
    Lagrangian run function for multiple processors
    """
    
    start = time.time()
    

    u4d = np.ctypeslib.as_array(s_u4d)
    v4d = np.ctypeslib.as_array(s_v4d)
    w4d = np.ctypeslib.as_array(s_w4d)
    lat1d = np.ctypeslib.as_array(s_lat1d)
    lon1d = np.ctypeslib.as_array(s_lon1d)

    if forward_flag ==1:
        end_timestamp=final_t
    else:
        end_timestamp=strt_t
    
    while(airp_lst[0].t[-1] < final_t): # not reach the final step
    

        # ***Elemental Operation of Lagrangian Model***
        # update global idt
        idt=int(round((len(airp_lst[0].t)-1)/inpf_per_dt,0))         
        curr_t=airp_lst[0].t[-1].strftime('%Y-%m-%d %H:%M:%S')
    
        print('TASK[%02d]: Lagrangian Run at %s' % ( itsk, curr_t))


        for airp in airp_lst:
            # resolve ix iy iz for the last (T+0) move
            core.lagrange.resolve_curr_xyz(airp, lat1d, lon1d, z4d[idt,:,:,:]) 
            
            idz=airp.iz[-1]
            idx=airp.ix[-1]
            idy=airp.iy[-1]
            # march all parcels (T+1)
            core.lagrange.lagrange_march(airp, u4d[idt,idz,idx,idy], v4d[idt,idz,idx,idy], w4d[idt, idz,idx,idy], dts)

    end = time.time()
    print('TASK[%02d] END: Lagrangian Run at %s, used %0.3f seconds' % (itsk, curr_t, (end - start)))
    return airp_lst

def create_share_type(np_array):
    np_carr = np.ctypeslib.as_ctypes(np_array)
    shared_array = sharedctypes.Array(np_carr._type_, np_carr, lock=False) 
    return shared_array

def _init(shared_u4d, shared_v4d, shared_w4d, shared_lat1d, shared_lon1d):
    """ Each pool process calls this initializer. Load the array to be populated into that process's global namespace """
    global s_u4d, s_v4d, s_w4d, s_lat1d, s_lon1d
    s_u4d=shared_u4d
    s_v4d=shared_v4d
    s_w4d=shared_w4d
    s_lat1d=shared_lat1d
    s_lon1d=shared_lon1d

def main_run():
    
    itsk=0
    print('Easy ERA5 Trac Start...')
    
    print('Read Config...')
    cfg_hdl=read_cfg('./conf/config.ini')
    
    print('Init Fields...')
    fields_hdl=lib.preprocess_era5inp.era5_acc_fields(cfg_hdl)
   
    print('Construct Input Air Parecels...')
    air_in_fhdl=pd.read_csv('./input/input.csv', names=['idx','lat0', 'lon0', 'h0'], index_col='idx')


    airp_lst=[] # all traced air parcelis packed into a list
    for row in air_in_fhdl.itertuples():
        airp_lst.append(lib.air_parcel.air_parcel(row.Index,row.lat0, row.lon0, row.h0, cfg_hdl, fields_hdl.strt_t))

    print('CORE Procedure: Lagrangian Tracing...')

    # ------Prepare inital parameters---
    idt=0 # initial timeframe

    inpf_per_dt= fields_hdl.drv_fld_dt # calculate input file frq per integ dt
    dts=airp_lst[0].dt.total_seconds() # dt in seconds

    ntasks=int(cfg_hdl['CORE']['ntasks'])
   

    # Whether multiplethreading would be used
    if len(airp_lst) > 1000:
        print('Master process %s.' % os.getpid())
        
        # Initial shared data
       
        shared_u4d = create_share_type(fields_hdl.U.values) 
        shared_v4d = create_share_type(fields_hdl.V.values) 
        shared_w4d = create_share_type(fields_hdl.W.values) 
        shared_lat1d = create_share_type(fields_hdl.xlat.values) 
        shared_lon1d = create_share_type(fields_hdl.xlon.values) 
        

        # start process pool
        process_pool = Pool(processes=ntasks, initializer=_init, initargs=(shared_u4d, shared_v4d,
            shared_w4d, shared_lat1d, shared_lon1d,))
         
        len_airp=len(airp_lst)
        len_per_task=len_airp//ntasks
        results = []

        # open tasks ID 0 to ntasks-2
        for itsk in range(ntasks-1):  
            results.append(process_pool.apply_async(lag_run_mtsk,args=(itsk, airp_lst[itsk*len_per_task:(itsk+1)*len_per_task], dts, inpf_per_dt, fields_hdl.forward, fields_hdl.strt_t, fields_hdl.final_t,)))

        # open ID ntasks-1 in case of residual
        results.append(process_pool.apply_async(lag_run_mtsk, args=(ntasks-1, airp_lst[(ntasks-1)*len_per_task:], dts,inpf_per_dt, fields_hdl.final_t,)))
        
        print('Waiting for all subprocesses done...')
        
        process_pool.close()
        process_pool.join()
        # reorg airp objs list
        airp_lst=[] 
        for res in results:
            airp_lst.extend(res.get())
        print('All subprocesses done.')
            
    else:
            
       u4d=fields_hdl.U.values
       v4d=fields_hdl.V.values
       w4d=fields_hdl.W.values
       z4d=fields_hdl.Z.values
       
       lag_run_seriel(0, airp_lst, u4d, v4d, w4d, z4d, fields_hdl.xlat.values, fields_hdl.xlon.values,  dts, inpf_per_dt, fields_hdl.final_t)
           
           # end if <Muiltiple, Seriel>

    print('Output...')
    lib.air_parcel.acc_output(airp_lst, 5000, cfg_hdl)



if __name__=='__main__':
    main_run()
