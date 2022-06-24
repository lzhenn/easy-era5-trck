#/usr/bin/env python3
'''
Date: May 29, 2020

Main script to drive the easy-era5-trck model


Revision:
Oct 28, 2020 --- MVP v0.01 completed
May 31, 2021 --- Major revision, v0.90 

Zhenning LI
'''
import cdsapi
import datetime
import json

import sys
sys.path.append('../')

import lib
import lib.utils as utils
import logging.config


def main_run():

    # logging manager
    logging.config.fileConfig('../conf/logging_config.ini')

    utils.write_log('Easy ERA5 Track Download Tool Start...')
    utils.write_log('Read Config...')
    cfg_hdl=lib.cfgparser.read_cfg('../conf/config.ini')
    
    repo_root=utils.get_root()

    lib.cfgparser.test_sanity_download(cfg_hdl)
    
    pres_lst=json.loads(cfg_hdl['DOWNLOAD']['pres'])
    area_lst=json.loads(cfg_hdl['DOWNLOAD']['area'])
    freq=cfg_hdl['DOWNLOAD']['freq_hr']

    int_time_obj = datetime.datetime.strptime(cfg_hdl['DOWNLOAD']['start_ymd'], '%Y%m%d')
    end_time_obj = datetime.datetime.strptime(cfg_hdl['DOWNLOAD']['end_ymd'], '%Y%m%d')
    file_time_delta=datetime.timedelta(days=1)
    curr_time_obj = int_time_obj

    c = cdsapi.Client()

    while curr_time_obj <= end_time_obj:
        c.retrieve(
            'reanalysis-era5-pressure-levels',
            {
                'product_type':'reanalysis',
                'format':'grib',
                'pressure_level':pres_lst,
                'date':curr_time_obj.strftime('%Y%m%d'),
                'area':area_lst,
                'time':'00/to/23/by/'+freq,
                'variable':[
                    'vertical_velocity','u_component_of_wind','v_component_of_wind'
                ]
            },
            '../'+cfg_hdl['DOWNLOAD']['store_path']+curr_time_obj.strftime('%Y%m%d')+'-pl.grib')
        utils.write_log(curr_time_obj.strftime('%Y-%m-%d')+' downloaded...')
        curr_time_obj=curr_time_obj+file_time_delta
    utils.write_log('All downloading tasks are completed!')

if __name__=='__main__':
    main_run()
