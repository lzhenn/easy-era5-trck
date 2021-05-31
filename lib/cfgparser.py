#/usr/bin/env python
"""configure script to get build parameters from user."""
import os
import configparser
import lib.utils as utils

print_prefix='lib.cfgparser>>'

def read_cfg(config_file):
    """ Simply read the config files """
    config=configparser.ConfigParser()
    config.read(config_file)
    return config

def write_cfg(cfg_hdl, config_fn):
    """ Simply write the config files """
    with open(config_fn, 'w') as configfile:
        cfg_hdl.write(configfile)

def test_sanity_run(cfg):
    """ test if the cfg file is valid for running"""
    
    
    # test input era5
    input_file=cfg['INPUT']['input_era5']+cfg['INPUT']['input_obv']
    if not(os.path.exists(input_file)):
        utils.throw_error(print_prefix, 'cannot locate:'+input_file+'')

    template_file='./db/'+cfg['INPUT']['input_wrf']
    
    # test wrf template exists
    if not(os.path.exists(template_file)):
        utils.throw_error(print_prefix, 'cannot locate:${EASY_ERA5_TRCK}/'+template_file)
    
    # test reasonable integration time
    t_interp=int(cfg['CORE']['interp_t_length'])
    if t_interp>120:
        utils.write_log(print_prefix+'interp_t_length='+str(t_interp)+' is larger than 120 hr',lvl=30)

    if t_interp>168 or t_interp<0:
        utils.throw_error(print_prefix,'interp_t_length='+str(t_interp)+', not allowed > 168 hr or < 0 hr')

    # test reasonable interp interval
    interp_interval=int(cfg['CORE']['interp_interval'])
    if interp_interval>180 or interp_interval<1:
        utils.throw_error(print_prefix,'interp_interval='+str(interp_interval)+', not allowed > 180 min or < 1 min')

def test_sanity_download(cfg):
    """ test if the cfg file is valid for downloading"""
    
    repo_root=utils.get_root()+'/'
    
    # test store_path exists
    store_path=cfg['DOWNLOAD']['store_path']
    if not(os.path.exists(repo_root+store_path)):
        utils.throw_error(print_prefix+'cannot locate:'+repo_root+store_path)

