#/usr/bin/env python
"""Commonly used utilities

    Function    
    ---------------
    throw_error(source, msg):
        Throw error with call source and error message

"""
import numpy as np
import logging
import lib.cfgparser
import os

DEG2RAD=np.pi/180.0

def throw_error(msg):
    '''
    throw error and exit
    '''
    logging.error(msg)
    logging.error('Abnormal termination of Easy ERA5 Trac!')

    exit()

def write_log(msg, lvl=20):
    '''
    write logging log to log file
    level code:
        CRITICAL    50
        ERROR   40
        WARNING 30
        INFO    20
        DEBUG   10
        NOTSET  0
    '''

    logging.log(lvl, msg)

def get_root():
    cfg=lib.cfgparser.read_cfg('../conf/config_sys.ini')
    if not(os.path.exists(cfg['SYS']['root'])):
        throw_error(cfg['SYS']['root']+' not found! Please check if config.py has been executed!')
    
    return cfg['SYS']['root']
