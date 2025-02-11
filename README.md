# era5_to_int

A simple Python script for converting ERA5 model-level netCDF files to the WPS
intermediate format

## Overview

The `era5_to_int.py` script converts ERA5 model-level netCDF files to the WRF
Pre-processing System (WPS) intermediate file format, permitting the use of
these data with either the Weather Research and Forecasting (WRF) model or the
Model for Prediction Across Scales - Atmosphere (MPAS-A).

The only required command-line argument is the date-time, in YYYY-MM-DD_HH
format, of ERA5 model-level files to process. With no optional arguments, the
script will search known paths on the NWSC Glade filesystem for ERA5 model-level
netCDF files. If the `-p`/`--path` option is provided with a local path, the
script will instead search that local path for ERA5 files that have been
downloaded from the NSF NCAR Research Data Archive (RDA) ds633 datasets.

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

Usage is provided by running the `era5_to_int.py` script with the `-h`/`--help`
argument, which prints the following:
```
  usage: era5_to_int.py [-h] [-p PATH] datetime

  positional arguments:
    datetime              the date-time to convert in YYYY-MM-DD_HH format

  options:
    -h, --help            show this help message and exit
    -p PATH, --path PATH  the local path to search for ERA5 netCDF files
```

Upon successful completion, an intermediate file with the prefix `ERA5` is
created in the current working directory; for example, `ERA5:2023-01-28_00`.

## Supplementary files

Included in this repository is a list of ECMWF vertical level coefficients in
the `ecmwf_coeffs` file. The `ecmwf_coeffs` file may be used with the WPS
`calc_ecmwf_p.exe` utility program to generate an intermediate file with 3-d
pressure, geopotential height, and R.H. fields.
