#/usr/bin/env python3
'''
Date: Oct 28, 2020

Main script to drive the easy-era5-trck model


Revision:
Oct 28, 2020 --- MVP v0.01 completed
May 31, 2021 --- Major revision, v0.90 


Zhenning LI
'''

import numpy as np
import pandas as pd
import os, sys, time

import  lib, core
import lib.utils as utils

import logging.config
from multiprocessing import Pool, sharedctypes

def main_run():
    
    # logging manager
    logging.config.fileConfig('./conf/logging_config.ini')
    
    itsk=0
    utils.write_log('Easy ERA5 Trac Start...')
    
    utils.write_log('Read Config...')
    cfg_hdl=lib.cfgparser.read_cfg('./conf/config.ini')
    
    if len(sys.argv)==2:
        utils.write_log('Catch external start_ymdh='+sys.argv[1])
        cfg_hdl['CORE']['start_ymdh']=sys.argv[1]

    utils.write_log('Init Fields...')
    fields_hdl=lib.preprocess_era5inp.era5_acc_fields(cfg_hdl)
   
    utils.write_log('Construct Input Air Parecels...')
    air_in_fhdl=pd.read_csv(cfg_hdl['INPUT']['input_parcel_file'], names=['idx','lat0', 'lon0', 'h0'], index_col='idx')

    airp_lst=[] # all traced air parcelis packed into a list
    for row in air_in_fhdl.itertuples():
        airp_lst.append(lib.air_parcel.air_parcel(row.Index,row.lat0, row.lon0, row.h0, cfg_hdl, fields_hdl.strt_t, fields_hdl.forward))

    utils.write_log('CORE Procedure: Lagrangian Tracing...')
    
    # ------Prepare inital parameters---
    # init parameter dict
    para_dic={
            'step_per_inpf': fields_hdl.step_per_inpf, # calculate input file frq per integ dt
            'inp_nfrm':fields_hdl.inp_nfrm,
            'forward':fields_hdl.forward,
            'dts':airp_lst[0].dt.total_seconds(), # dt in seconds
            'strt_t':fields_hdl.strt_t,
            'final_t': fields_hdl.final_t,
            'xz': fields_hdl.xz.values
            }


    ntasks=int(cfg_hdl['CORE']['ntasks'])
   

    # Whether multiplethreading would be used
    if (len(airp_lst) > 1000) and (ntasks>1):
        utils.write_log('Master process %s.' % os.getpid())
        
        # Initial shared data
       
        shared_u4d,shared_v4d, shared_w4d = create_share_type(fields_hdl.U.values), create_share_type(fields_hdl.V.values), create_share_type(fields_hdl.W.values) 
        shared_lat1d,shared_lon1d = create_share_type(fields_hdl.xlat.values), create_share_type(fields_hdl.xlon.values) 
         
        
        # start process pool
        process_pool = Pool(processes=ntasks, initializer=_init, initargs=(shared_u4d, shared_v4d,
            shared_w4d, shared_lat1d, shared_lon1d,))
         
        len_airp=len(airp_lst)
        len_per_task=len_airp//ntasks
        results = []

        # open tasks ID 0 to ntasks-2
        for itsk in range(ntasks-1):  
            results.append(process_pool.apply_async(lag_run_mtsk,args=(itsk, airp_lst[itsk*len_per_task:(itsk+1)*len_per_task], para_dic,)))

        # open ID ntasks-1 in case of residual
        results.append(process_pool.apply_async(lag_run_mtsk, args=(ntasks-1, airp_lst[(ntasks-1)*len_per_task:], para_dic,)))
        
        utils.write_log('Waiting for all subprocesses done...')
        
        process_pool.close()
        process_pool.join()
        # reorg airp objs list
        airp_lst=[] 
        for res in results:
            airp_lst.extend(res.get())
        utils.write_log('All subprocesses done.')
            
    else:
       u4d, v4d, w4d=fields_hdl.U.values, fields_hdl.V.values, fields_hdl.W.values
       lag_run_seriel(0, airp_lst, u4d, v4d, w4d, fields_hdl.xlat.values, fields_hdl.xlon.values, para_dic)
           
    # end if <Muiltiple, Seriel>

    utils.write_log('Output...')

    lib.air_parcel.acc_output(airp_lst, cfg_hdl)
    
    utils.write_log('Easy ERA5 Track Completed Successfully!')


def lag_run_seriel(itsk, airp_lst, u4d, v4d, w4d, lat1d, lon1d, para_dic):
    """
    Lagrangian run function for seriel processor
    """
    
    start = time.time()
    
    while(airp_lst[0].t[-1] != para_dic['final_t']): # not reach the final step

        # ----------***Elemental Operation of Lagrangian Model***-----------
        
        # update global idt (which frame of the data)
        idt=int(round((len(airp_lst[0].t)-1)/para_dic['step_per_inpf'],0))         
        
        if para_dic['forward']==-1:
            idt=para_dic['inp_nfrm']-idt-1

        curr_t=airp_lst[0].t[-1].strftime('%Y-%m-%d %H:%M:%S')
    
        utils.write_log('TASK[%02d]: Lagrangian Run at %s' % ( itsk, curr_t))

        for airp in airp_lst:
            # resolve ix iy iz for the last (T+0) move
            core.lagrange.resolve_curr_xyz(airp, lat1d, lon1d, para_dic['xz']) 
            
            idz=airp.iz[-1]
            idx=airp.ix[-1]
            idy=airp.iy[-1]
            # march all parcels (T+1)
            core.lagrange.lagrange_march(airp, u4d[idt,idz,idx,idy], v4d[idt,idz,idx,idy], w4d[idt, idz,idx,idy], para_dic['dts'])
        
        # ----------***Elemental Operation of Lagrangian Model***-----------

    curr_t=airp_lst[0].t[-1].strftime('%Y-%m-%d %H:%M:%S')
    end = time.time()
    
    utils.write_log('TASK[%02d]: Lagrangian Run at %s, completed with %0.3f seconds elapsed.' % (itsk, curr_t, (end - start)))

def lag_run_mtsk(itsk, airp_lst, para_dic):
    """
    Lagrangian run function for multiple processors
    """
    
    start = time.time()
    u4d = np.ctypeslib.as_array(s_u4d)
    v4d = np.ctypeslib.as_array(s_v4d)
    w4d = np.ctypeslib.as_array(s_w4d)
    lat1d = np.ctypeslib.as_array(s_lat1d)
    lon1d = np.ctypeslib.as_array(s_lon1d)

    while(airp_lst[0].t[-1] != para_dic['final_t']): # not reach the final step


        # ----------***Elemental Operation of Lagrangian Model***-----------
        
        
        # update global idt (which frame of the data)
        idt=int(round((len(airp_lst[0].t)-1)/para_dic['step_per_inpf'],0))         
        
        if para_dic['forward']==-1:
            idt=para_dic['inp_nfrm']-idt-1

        curr_t=airp_lst[0].t[-1].strftime('%Y-%m-%d %H:%M:%S')
    
        utils.write_log('TASK[%02d]: Lagrangian Run at %s' % ( itsk, curr_t))

        for airp in airp_lst:
            # resolve ix iy iz for the last (T+0) move
            core.lagrange.resolve_curr_xyz(airp, lat1d, lon1d, para_dic['xz']) 
            
            idz=airp.iz[-1]
            idx=airp.ix[-1]
            idy=airp.iy[-1]
            # march all parcels (T+1)
            core.lagrange.lagrange_march(airp, u4d[idt,idz,idx,idy], v4d[idt,idz,idx,idy], w4d[idt, idz,idx,idy], para_dic['dts'])
        # ----------***Elemental Operation of Lagrangian Model***-----------
    
    curr_t=airp_lst[0].t[-1].strftime('%Y-%m-%d %H:%M:%S')
    end = time.time()
    utils.write_log('TASK[%02d]: Lagrangian Run at %s, completed with %0.3f seconds elapsed.' % (itsk, curr_t, (end - start)))
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



if __name__=='__main__':
    main_run()
