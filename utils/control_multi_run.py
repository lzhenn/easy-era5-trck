#/usr/bin/env python
'''
Date: May 30, 2021

auto run for multiple start_ymdh 

PLEASE FIRST SET OTHER PARAMETERS IN config.ini properly 
before run this script, this script run multiple times
by overwriting [CORE]['start_ymdh'] in config.ini

Zhenning LI

'''

import sys, os
import datetime
sys.path.append('../')
import lib
import lib.utils as utils

#------set global attributes below------

# The first [CORE]['start_ymdh'] in config.ini
series_first_ymdh = '2015123100'

# The last [CORE]['start_ymdh'] in config.ini
series_last_ymdh = '2016010500'

# interval hours between each 'start_ymdh'
series_delta_hr = 24

#------set global attributes above------

#------EXCECUTION-------
# The first initial time
ini_date=datetime.datetime.strptime(series_first_ymdh,'%Y%m%d%H')

# The final initial time
final_date=datetime.datetime.strptime(series_last_ymdh,'%Y%m%d%H')

# Interval between each initial time
delta_hr=datetime.timedelta(hours=series_delta_hr)

cfg_hdl=lib.cfgparser.read_cfg('../conf/config.ini')
curr_date=ini_date
while curr_date <= final_date:
    print('>>>>>>>>>>>>>>Multi_Run @ '+curr_date.strftime('%Y%m%d%H')+'<<<<<<<<<<<<<<<<')
    
    # execute run script
    os.system('cd '+utils.get_root()+'; python3 run.py '+curr_date.strftime('%Y%m%d%H'))
    curr_date=curr_date+delta_hr


