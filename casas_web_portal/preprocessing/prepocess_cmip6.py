#!/usr/bin/env python3

import os
import sys
import pandas as pd
import geopandas as gpd
import numpy as np

from casas_web_portal.functions import read_nc
# Relative humidity from Tmax and Tmin (Thornton et al. 1997)
def tmaxmin2rh(tmax, tmin):
    em = 610.78 * np.exp((17.269 * tmin) / (237.3 + tmin))
    tavg = (tmax + tmin) / 2
    es = 610.78 * np.exp((17.269 * tavg) / (237.3 + tavg))
    rh = em / es
    rh = np.clip(rh, 0, 1)
    return rh

# Main function
def write_casas_wx(bbox, start, end, indir, outdir):

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    nc_tmax = read_nc("tasmax")
    nc_tmin = read_nc("tasmin")
    nc_prcp = read_nc("pr")

    time_units = nc_tmax.variables['time'].units
    calendar = getattr(nc_tmax.variables['time'], 'calendar', 'proleptic_gregorian')
    time_values = num2date(nc_tmax.variables['time'][:], units=time_units, calendar=calendar)

    tmax = nc_tmax.variables['tasmax'][x, y, :]
    tmin = nc_tmin.variables['tasmin'][x, y, :]
    prcp = nc_prcp.variables['pr'][x, y, :] * 86400  # kg/m2/s to mm/day

    rh = tmaxmin2rh(tmax, tmin) * 100
    tmax_c = tmax - 273.15
    tmin_c = tmin - 273.15
    prcp = np.clip(prcp, 0, None)

    for i, date in enumerate(time_values):
        line = f"{date.month:02d}\t{date.day:02d}\t{date.year}" \
                f"\t{tmax_c[i]:.1f}\t{tmin_c[i]:.1f}\t-99\t{prcp[i]:.1f}\t{rh[i]:.1f}\t-99\n"
        f.write(line)

    nc_tmax.close()
    nc_tmin.close()
    nc_prcp.close()

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 9:
        print("Usage: script.py <start_subset> <end_subset> <workdir> <outdir> <geofile> <start_year> <end_year> <time_origin> <run_label>")
        sys.exit(1)

    get_casas_wx(
        start_subset=int(args[0]),
        end_subset=int(args[1]),
        workdir=args[2],
        outdir=args[3],
        geofile=args[4],
        start_year=int(args[5]),
        end_year=int(args[6]),
        time_origin=args[7],
        run_label=args[8]
    )
