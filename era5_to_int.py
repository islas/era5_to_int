#!/usr/bin/env python3


def days_in_month(year, month):
    """ Returns the number of days in a month, depending on the year.
    A Gregorian calendar is assumed for the purposes of determining leap
    years.
    """
    non_leap_year = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
    leap_year     = [ 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]

    if (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0)):
        return leap_year[month - 1]
    else:
        return non_leap_year[month - 1]


def intdate_to_string(utc_int):
    """ Converts an integer date representation into a string.
    The digits of utc_int represent yyyymmddhh, and the returned string
    is of the form 'yyyy-mm-dd_hh:00:00'.
    """
    year = utc_int // 1000000
    month = (utc_int // 10000) % 100
    day = (utc_int // 100) % 100
    hour = utc_int % 100
    return '{:04d}-{:02d}-{:02d}_{:02d}:00:00'.format(year, month, day, hour)


def begin_6hourly(yyyy, mm, dd, hh):
    """ Returns a date-time string of the form yyyymmddhh for the year, month,
    day, and hour with the hours rounded down the the beginning of a six-hour
    interval, i.e., 0, 6, 12, and 18.
    """
    return f'{yyyy:04d}{mm:02d}{dd:02d}{((hh // 6) * 6):02d}'


def end_6hourly(yyyy, mm, dd, hh):
    """ Returns a date-time string of the form yyyymmddhh for the year, month,
    day, and hour with the hours rounded up the the last hour of a six-hour
    interval, i.e., 5, 11, 17, and 23.
    """
    return f'{yyyy:04d}{mm:02d}{dd:02d}{((hh // 6) * 6 + 5):02d}'


def begin_monthly(yyyy, mm, dd, hh):
    """ Returns a date-time string of the form yyyymmddhh for the year, month,
    day, and hour with the day and hour rounded down the the beginning of a
    monthly interval.
    """
    return f'{yyyy:04d}{mm:02d}{1:02d}{0:02d}'


def end_monthly(yyyy, mm, dd, hh):
    """ Returns a date-time string of the form yyyymmddhh for the year, month,
    day, and hour with the day and hour rounded up the the last day and hour
    of the month.
    """
    return f'{yyyy:04d}{mm:02d}{days_in_month(yyyy,mm):02d}{23:02d}'


class MapProjection:
    """ Stores parameters of map projections as used in the WPS intermediate
    file format.
    """

    def __init__(self, projType, startLat, startLon, startI, startJ,
                 deltaLat, deltaLon,
                 dx=0.0, dy=0.0, truelat1=0.0, truelat2=0.0, xlonc=0.0):
        self.projType = projType
        self.startLat = startLat
        self.startLon = startLon
        self.startI = startI
        self.startJ = startJ
        self.deltaLat = deltaLat
        self.deltaLon = deltaLon
        self.dx = dx
        self.dy = dy
        self.truelat1 = truelat1
        self.truelat2 = truelat2
        self.xlonc = xlonc


class MetVar:
    """ Describes a variable to be converted from netCDF to intermediate file
    format.
    """

    def __init__(self, WPSname, ERA5name, ERA5file, beginDateFn, endDateFn,
                 mapProj, isInvariant=False):
        self.WPSname = WPSname
        self.ERA5name = ERA5name
        self.ERA5file = ERA5file
        self.beginDateFn = beginDateFn
        self.endDateFn = endDateFn
        self.mapProj = mapProj
        self.isInvariant = isInvariant


def find_era5_file(var, validtime, localpaths=None):
    """ Returns a filename with path information of an ERA5 netCDF file given
    the ERA5 netCDF variable name and the valid time of the variable.
    The localpaths argument may be used to specify an array of local
    directories to search for ERA5 netCDF files. If localpaths is not provided
    or is None, known paths on the NWSC Glade filesystem are searched.
    If no file can be found containing the specified variable at the specified
    time an empty string is returned.
    """
    import os.path

    glade_paths = [
        '/glade/campaign/collections/rda/data/ds633.6/e5.oper.an.ml/',
        '/glade/campaign/collections/rda/data/ds633.0/e5.oper.an.sfc/',
        '/glade/campaign/collections/rda/data/ds633.0/e5.oper.invariant/197901/',
        '/gpfs/csfs1/collections/rda/decsdata/ds630.0/P/e5.oper.invariant/201601/'
        ]

    if localpaths != None:
        file_paths = localpaths
    else:
        file_paths = glade_paths

    tmp = validtime.split('-')
    yyyy = int(tmp[0])
    mm = int(tmp[1])
    ddhh = tmp[2]
    dd = int(ddhh.split('_')[0])
    hh = int(ddhh.split('_')[1])

    begin_date = var.beginDateFn(yyyy, mm, dd, hh)
    end_date = var.endDateFn(yyyy, mm, dd, hh)

    for p in file_paths:
        if var.isInvariant or localpaths != None:
            # For time-invariant fields, or if we are searching local paths,
            # assume that there is no need to append yyyymm to the end of
            # directories.
            base_path = p
        else:
            base_path = p + f'{yyyy:04d}{mm:02d}/'

        filename = base_path + var.ERA5file.format(begin_date, end_date)
        if os.path.isfile(filename):
            return filename

    return ''


def find_time_index(ncfilename, validtime):
    """ Returns a 0-based offset into the unlimited dimension of the specified
    valid time within the specified etCDF file.
    If the specified time is not found in the file, an offset of -1 is
    returned.
    The 'utc_date' variable is assumed to exist in the netCDF file, and it is
    through this variable that the search for the valid time takes place.
    """
    from netCDF4 import Dataset
    import numpy as np

    tmp = validtime.split('-')
    yyyy = int(tmp[0])
    mm = int(tmp[1])
    ddhh = tmp[2]
    dd = int(ddhh.split('_')[0])
    hh = int(ddhh.split('_')[1])

    needed_date = yyyy * 1000000 + mm * 10000 + dd * 100 + hh

    with Dataset(ncfilename) as f:
        utc_date = f.variables['utc_date'][:]

        idx = np.where(needed_date == utc_date)
        if idx[0].size == 0:
            return -1
        else:
            return idx[0][0]


def write_slab( intfile, slab, xlvl, proj, WPSname, hdate, units, map_source, desc):
    """ Writes a 2-d array (a 'slab' of data) to an opened intermediate file
    using the provided level, projection, and other metadata.
    This routine assumes that the intermediate file has already been created
    through a previous call to the WPSUtils.intermediate.write_met_init
    routine.
    """
    stat = intfile.write_next_met_field(
        5, slab.shape[1], slab.shape[0], proj.projType, 0.0, xlvl,
        proj.startLat, proj.startLon, proj.startI, proj.startJ,
        proj.deltaLat, proj.deltaLon, proj.dx, proj.dy, proj.xlonc,
        proj.truelat1, proj.truelat2, 6371229.0, 0, v.WPSname,
        hdate, units, map_source, desc, slab)


def add_trailing_slash(str):
    """ Returns str with a forward slash appended to it if the str argument does
    not end with a forward slash character. Otherwise, return str unmodified if
    it already ends with a slash.
    """
    if str[-1] == '/':
        return str
    else:
        return str + '/'


if __name__ == '__main__':
    from netCDF4 import Dataset
    import numpy as np
    import WPSUtils
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('datetime', help='the date-time to convert in YYYY-MM-DD_HH format')
    parser.add_argument('-p', '--path', help='the local path to search for ERA5 netCDF files')
    args = parser.parse_args()

    initdate = args.datetime

    # Set up the two map projections used in the ERA5 fields to be converted
    Gaussian = MapProjection(WPSUtils.Projections.GAUSS,
         89.7848769072, 0.0, 1.0, 1.0, 640.0 / 2.0, 360.0 / 1280.0)
    LatLon = MapProjection(WPSUtils.Projections.LATLON,
         90.0, 0.0, 1.0, 1.0, -0.25, 0.25)

    int_vars = []
    int_vars.append(MetVar('SPECHUMD', 'Q', 'e5.oper.an.ml.0_5_0_1_0_q.regn320sc.{}_{}.nc', begin_6hourly, end_6hourly, Gaussian))
    int_vars.append(MetVar('TT', 'T', 'e5.oper.an.ml.0_5_0_0_0_t.regn320sc.{}_{}.nc', begin_6hourly, end_6hourly, Gaussian))
    int_vars.append(MetVar('UU', 'U', 'e5.oper.an.ml.0_5_0_2_2_u.regn320uv.{}_{}.nc', begin_6hourly, end_6hourly, Gaussian))
    int_vars.append(MetVar('VV', 'V', 'e5.oper.an.ml.0_5_0_2_3_v.regn320uv.{}_{}.nc', begin_6hourly, end_6hourly, Gaussian))
    int_vars.append(MetVar('LANDSEA', 'LSM', 'e5.oper.invariant.128_172_lsm.ll025sc.1979010100_1979010100.nc', begin_monthly, end_monthly, LatLon, isInvariant=True))
    int_vars.append(MetVar('SST', 'SSTK', 'e5.oper.an.sfc.128_034_sstk.ll025sc.{}_{}.nc', begin_monthly, end_monthly, LatLon))
    int_vars.append(MetVar('SKINTEMP', 'SKT', 'e5.oper.an.sfc.128_235_skt.ll025sc.{}_{}.nc', begin_monthly, end_monthly, LatLon))
    int_vars.append(MetVar('SM000007', 'SWVL1', 'e5.oper.an.sfc.128_039_swvl1.ll025sc.{}_{}.nc', begin_monthly, end_monthly, LatLon))
    int_vars.append(MetVar('SM007028', 'SWVL2', 'e5.oper.an.sfc.128_040_swvl2.ll025sc.{}_{}.nc', begin_monthly, end_monthly, LatLon))
    int_vars.append(MetVar('SM028100', 'SWVL3', 'e5.oper.an.sfc.128_041_swvl3.ll025sc.{}_{}.nc', begin_monthly, end_monthly, LatLon))
    int_vars.append(MetVar('SM100289', 'SWVL4', 'e5.oper.an.sfc.128_042_swvl4.ll025sc.{}_{}.nc', begin_monthly, end_monthly, LatLon))
    int_vars.append(MetVar('ST000007', 'STL1', 'e5.oper.an.sfc.128_139_stl1.ll025sc.{}_{}.nc', begin_monthly, end_monthly, LatLon))
    int_vars.append(MetVar('ST007028', 'STL2', 'e5.oper.an.sfc.128_170_stl2.ll025sc.{}_{}.nc', begin_monthly, end_monthly, LatLon))
    int_vars.append(MetVar('ST028100', 'STL3', 'e5.oper.an.sfc.128_183_stl3.ll025sc.{}_{}.nc', begin_monthly, end_monthly, LatLon))
    int_vars.append(MetVar('ST100289', 'STL4', 'e5.oper.an.sfc.128_236_stl4.ll025sc.{}_{}.nc', begin_monthly, end_monthly, LatLon))
    int_vars.append(MetVar('SEAICE', 'CI', 'e5.oper.an.sfc.128_031_ci.ll025sc.{}_{}.nc', begin_monthly, end_monthly, LatLon))
    int_vars.append(MetVar('PSFC', 'SP', 'e5.oper.an.ml.128_134_sp.regn320sc.{}_{}.nc', begin_6hourly, end_6hourly, Gaussian))
    int_vars.append(MetVar('SOILGEO', 'Z', 'e5.oper.invariant.128_129_z.regn320sc.2016010100_2016010100.nc', begin_monthly, end_monthly, Gaussian, isInvariant=True))

    intfile = WPSUtils.IntermediateFile('ERA5', initdate)

    if args.path != None:
        paths = [ add_trailing_slash(p) for p in args.path.split(',') ]
    else:
        paths = None

    for v in int_vars:
        e5filename = find_era5_file(v, initdate, localpaths=paths)
        idx = find_time_index(e5filename, initdate)
        if idx == -1:
            idx = 0
        proj = v.mapProj

        print(e5filename)
        with Dataset(e5filename) as f:
            hdate = intdate_to_string(f.variables['utc_date'][idx])
            print('Converting ' + v.WPSname + ' at ' + hdate)
            map_source = 'ERA5 reanalysis grid          '
            units = f.variables[v.ERA5name].units
            desc = f.variables[v.ERA5name].long_name
            field_arr = f.variables[v.ERA5name][idx,:]

            if field_arr.ndim == 2:
                slab = field_arr
                xlvl = 200100.0
                if v.WPSname == 'SOILGEO':
                    xlvl = 1.0
                write_slab(intfile, slab, xlvl, proj, v.WPSname, hdate, units,
                    map_source, desc)
            else:
                for k in range(f.dimensions['level'].size):
                    slab = field_arr[k,:,:]
                    write_slab(intfile, slab, float(f.variables['level'][k]), proj,
                        v.WPSname, hdate, units, map_source, desc)

    intfile.close()
