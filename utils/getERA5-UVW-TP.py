import cdsapi
import datetime

int_time_obj = datetime.datetime.strptime('20150830', '%Y%m%d')
end_time_obj = datetime.datetime.strptime('20150930', '%Y%m%d')
file_time_delta=datetime.timedelta(days=1)
curr_time_obj = int_time_obj

c = cdsapi.Client()

while curr_time_obj <= end_time_obj:
    c.retrieve(
        'reanalysis-era5-pressure-levels',
        {
            'product_type':'reanalysis',
            'format':'grib',
            'pressure_level':[
                '200',
                '300',
                '400',
                '500','550','600',
                '650','700','750',
                '800',
                '850','900',
                '925',
                '1000'
            ],
            'date':curr_time_obj.strftime('%Y%m%d'),
            'area':[80,0,-15,150],
            'time':[
                '00:00',
                '03:00',
                '06:00',
                '09:00',
                '12:00',
                '15:00',
                '18:00',
                '21:00',
            ],
            'variable':[
                'vertical_velocity','u_component_of_wind','v_component_of_wind'
            ]
        },
        curr_time_obj.strftime('%Y%m%d')+'-pl.grib')
    curr_time_obj=curr_time_obj+file_time_delta
