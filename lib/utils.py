#/usr/bin/env python
"""Commonly used utilities

    Function    
    ---------------
    throw_error(source, msg):
        Throw error with call source and error message

"""
import numpy as np
import logging

DEG2RAD=np.pi/180.0

def throw_error(source, msg):
    '''
    throw error and exit
    '''
    logging.error(source+msg)
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
