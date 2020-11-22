# Easy-ERA5-Trck

Easy-ERA5-Trck is a super lightweight Lagrangian model for calculating thousands (even millions) of trajectories simultaneously and efficiently using ERA5 data sets. 
It implements super simplified equations of 3-D motion to accelerate integration, and python multiprocessing to parallelize the integration tasks.
Due to its simplification and parallelization, Easy-ERA5-Trck performs great speed in tracing massive air parcels, which makes **areawide** tracing possible.

Another version using WRF output to drive the model can be found [here](https://github.com/Novarizark/easy-wrf-trck). 

**Caution: Trajectory calculation is based on the nearest-neighbor interpolation and first-guess velocity for super efficiency. Accurate calculation algorithm can be found on http://journals.ametsoc.org/doi/abs/10.1175/BAMS-D-14-00110.1, or use a professional and complicated model e.g. [NOAA HYSPLIT](https://www.ready.noaa.gov/HYSPLIT.php) instead.**

**Any question, please contact Zhenning LI (zhenningli91@gmail.com)**

### Galleries

#### Tibetan Plateau Air Source Tracers
<img src="https://raw.githubusercontent.com/Novarizark/easy-era5-trck/master/gallery/tp.source.result.gif" alt="tp_tracer" align=center />

### Input Files

#### input.csv
`./input/input.csv`: This file prescribe the mass points for trajectory calculations. The style of this file:

```
mass_id, init_lat, init_lon, init_h0 (m)
```

#### configure.ini
`./conf/config.ini`: Configure file for the model. You may set WRF input file, input frequency, integration time steps, and other settings in this file.


### Module Files

#### run.py
`./run.py`: Main script to run the Easy-WRF-Trck. 

#### lagrange.py
`./core/lagrange.py`: Core module for calculating the mass points Lagrangian trajectories.

#### air_parcel.py
`./lib/air_parcel.py`: Module file containing definition of air parcel class and related group functions.

#### cfgparser.py
`./lib/cfgparser.py`: Module file containing read/write method of the `config.ini`

#### preprocess_wrfinp.py
`./lib/preprocess_wrfinp.py`: Module file that defines the field_hdl class, which contains useful fields data (U, V, W...) and related method, including wrfout IO operations.

