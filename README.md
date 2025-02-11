# era5_to_int

A simple Python script for converting ERA5 model-level netCDF files to the WPS
intermediate format

## Overview

The `era5_to_int.py` script converts ERA5 model-level netCDF files to the WRF
Pre-processing System (WPS) intermediate file format, permitting the use of
these data with either the Weather Research and Forecasting (WRF) model or the
Model for Prediction Across Scales - Atmosphere (MPAS-A).

*At present*, the script is designed to be run on a system that has access to
the NWSC Glade filesystem -- for example, Casper or Derecho -- and the ERA5
model-level netCDF files are assumed to be those provided by the ds633 datasets.

The following fields from the ds633 datasets are handled by the script:

| Field   | Dataset | Horiz. grid | Num. levels |
|---------|---------|-------------|-------------|
| Q       | [d633006](https://rda.ucar.edu/datasets/d633006/) | ~0.281-deg Gaussian | 137 |
| T       | [d633006](https://rda.ucar.edu/datasets/d633006/) | ~0.281-deg Gaussian | 137 |
| U       | [d633006](https://rda.ucar.edu/datasets/d633006/) | ~0.281-deg Gaussian | 137 |
| V       | [d633006](https://rda.ucar.edu/datasets/d633006/) | ~0.281-deg Gaussian | 137 |
| SOILGEO | [d633000](https://rda.ucar.edu/datasets/d633000/) | ~0.281-deg Gaussian | 1 |
| SP      | [d633006](https://rda.ucar.edu/datasets/d633006/) | ~0.281-deg Gaussian | 1 |
| LSM     | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |
| SSTK    | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |
| SKT     | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |
| SWVL1   | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |
| SWVL2   | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |
| SWVL3   | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |
| SWVL4   | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |
| STL1    | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |
| STL2    | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |
| STL3    | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |
| STL4    | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |
| CI      | [d633000](https://rda.ucar.edu/datasets/d633000/) | 0.25-deg Lat-Lon | 1 |

As fields are converted from netCDF to intermediate format, their names are also
converted to match WPS and MPAS-A expectations.

## Requirements
The `era5_to_int.py` script requires:
- Python 3.11+
- netCDF4
- NumPy

## Usage

The `era5_to_int.py` script takes a single command-line argument, which is the
valid date-time to be processed. This date-time is specified in `YYYY-MM-DD_HH`
format. For example:

```
era5_to_int.py 2023-01-28_00
```

Upon successful completion, an intermediate file with the prefix `ERA5` is
created in the current working directory; for example, `ERA5:2023-01-28_00`.

## Supplementary files

Included in this repository is a list of ECMWF vertical level coefficients in
the `ecmwf_coeffs` file. The `ecmwf_coeffs` file may be used with the WPS
`calc_ecmwf_p.exe` utility program to generate an intermediate file with 3-d
pressure, geopotential height, and R.H. fields.
