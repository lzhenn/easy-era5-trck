#/usr/bin/env python3
'''
Date: May 29, 2021

Initial config for fundamental parameters

Zhenning LI
'''

import os
import lib

sys_cfg_fn='./conf/config_sys.ini'
cfg_sys=lib.cfgparser.read_cfg(sys_cfg_fn)
cfg_sys['SYS']['root']=os.getcwd()
lib.cfgparser.write_cfg(cfg_sys, sys_cfg_fn)

