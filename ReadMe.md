
# Easy-ERA5-Trck

Easy-ERA5-Trck is a super lightweight Lagrangian model for calculating thousands (even millions) of trajectories simultaneously and efficiently using ERA5 data sets. 
It can implement super simplified equations of 3-D motion to accelerate integration, and use python multiprocessing to parallelize the integration tasks.
Due to its simplification and parallelization, Easy-ERA5-Trck performs great speed in tracing massive air parcels, which makes **areawide** tracing possible.

Another version using WRF output to drive the model can be found [here](https://github.com/Novarizark/easy-wrf-trck). 

**Caution: Trajectory calculation is based on the nearest-neighbor interpolation and first-guess velocity for super efficiency. Accurate calculation algorithm can be found on http://journals.ametsoc.org/doi/abs/10.1175/BAMS-D-14-00110.1, or use a professional and complicated model e.g. [NOAA HYSPLIT](https://www.ready.noaa.gov/HYSPLIT.php) instead.**

**Any question, please contact Zhenning LI (zhenningli91@gmail.com)**

### Galleries

#### Tibetan Plateau Air Source Tracers
<img src="https://raw.githubusercontent.com/Novarizark/easy-era5-trck/master/gallery/tp.source.result.gif" alt="tp_tracer" align=center />

#### Tibetan Plateau Air Source Tracers (3D)
<img src="https://github.com/Novarizark/easy-era5-trck/blob/master/gallery/tp.source.result.3d.gif?raw=true" alt="tp_tracer_3d" align=center />

### Install

If you wish to run easy-era5-trck using `grib2` data, Please first install [ecCodes](https://confluence.ecmwf.int/display/ECC/ecCodes+Home).

Please instal python3 using Anaconda3 distribution. [Anaconda3](https://www.anaconda.com/products/individual) with python3.8 has been fully tested, lower version of python3 may also work (without testing).

Now, we recommend to create a new environment in Anaconda and install the `requirements.txt`:

```
conda create -n test_era5trck python=3.8
conda activate test_era5trck
pip install -r requirements.txt
```


### Input Files

#### input.csv
`./input/input.csv`: This file prescribe the air parcels for trajectory simulation. The format of this file:

```
airp_id, init_lat, init_lon, init_h0 (hPa)
```

For forward trajectory, the init_{lat|lon|h0} denote initial positions; while for backward trajectory, they indicate ending positions.


#### config.ini
`./conf/config.ini`: Configure file for the model. You may set ERA5 input file, input frequency, integration time steps, and other settings in this file.


### Module Files

#### run.py
`./run.py`: Main script to run the Easy-ERA5-Trck. 

#### lagrange.py
`./core/lagrange.py`: Core module for calculating the air parcels Lagrangian trajectories.

#### air_parcel.py
`./lib/air_parcel.py`: Module file containing definition of air parcel class and related methods such as march and output.

#### cfgparser.py
`./lib/cfgparser.py`: Module file containing read/write method of the `config.ini`

#### preprocess_era5inp.py
`./lib/preprocess_era5inp.py`: Module file that defines the field_hdl class, which contains useful fields data (U, V, W...) and related method, including ERA5 grib file IO operations.

### Output Files

You could choose output files as plain ascii csv format or netCDF format (Recommended). netCDF format output metadata looks like:
``` bash
netcdf meiyu.ynl.I19980610000000.E19980605000000 {
dimensions:
    time = 121 ;
    parcel_id = 413 ;
variables:
    double xlat(time, parcel_id) ;
        xlat:_FillValue = NaN ;
    double xlon(time, parcel_id) ;
        xlon:_FillValue = NaN ;
    double xh(time, parcel_id) ;
        xh:_FillValue = NaN ;
    int64 time(time) ;
        time:units = "hours since 1998-06-10 00:00:00" ;
        time:calendar = "proleptic_gregorian" ;
    int64 parcel_id(parcel_id) ;
}
```

