import cdsapi
import datetime

archive_path='/home/metctm1/array/data/era5/LYN-Meiyu/'
int_time_obj = datetime.datetime.strptime('20200605', '%Y%m%d')
end_time_obj = datetime.datetime.strptime('20200720', '%Y%m%d')
file_time_delta=datetime.timedelta(days=1)
curr_time_obj = int_time_obj

c = cdsapi.Client()

while curr_time_obj <= end_time_obj:
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type':'reanalysis',
            'format':'grib',
            'date':curr_time_obj.strftime('%Y%m%d'),
           'area': [
            70, 60, -15,
            160], 
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
                'surface_pressure'
            ]
        },
        archive_path+curr_time_obj.strftime('%Y%m%d')+'-sl.grib')
    curr_time_obj=curr_time_obj+file_time_delta
