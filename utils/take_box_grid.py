#/usr/bin/env python
'''
Date: May 30, 2021

Take a rectanguler lat-lon box with specified size

Zhenning LI

'''

import numpy as np
import csv

#------set global attributes below------

# rectanguler box
start_lat, start_lon, end_lat, end_lon=18, 95, 55, 135

# rectanguler size
len_we, len_sn=161, 149 

# destination/starting height
aim_height=950

# set input.csv file name
csv_fn='../input/input_china_east_lv2.csv'

#------set global attributes above------


def main():

    xlat1d=np.linspace(start_lat, end_lat, len_sn)
    xlon1d=np.linspace(start_lon, end_lon, len_we)
    
    igrid=0
    with open(csv_fn, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        for ilat in xlat1d:
            for ilon in xlon1d:
                spamwriter.writerow([igrid, ilat, ilon, aim_height])
                igrid=igrid+1
 
    print('Done! please check: '+csv_fn)

if __name__ == "__main__":

    main()
       
