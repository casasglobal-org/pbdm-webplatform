#!/usr/bin/env python3
"""
Diagnostic tool for NetCDF files to help troubleshoot grid extraction issues.
Works in conjunction with netcdf_grid_extract.py and netcdf_grid_info.py.

Author: Luigi Ponti quartese gmail.com
Copyright: (c) 2025 CASAS (Center for the Analysis of Sustainable Agricultural
    Systems, https://www.casasglobal.org/)
SPDX-License-Identifier: GPL-3.0-or-later
"""

import xarray as xr
import numpy as np
import argparse
import sys
from pathlib import Path


def analyze_variable(ds, var_name, time_index=0):
    """Analyze a specific variable in the dataset."""
    var = ds[var_name]

    print(f"\nANALYZING VARIABLE: {var_name}")
    print("=" * 80)

    # Basic information
    print("\nBasic Information:")
    print(f"  Dimensions: {var.dims}")
    print(f"  Shape: {var.shape}")
    print(f"  Data type: {var.dtype}")

    # Attributes
    print("\nAttributes:")
    for attr, value in var.attrs.items():
        print(f"  {attr}: {value}")

    # Load a time slice if time dimension exists
    if 'time' in var.dims:
        data = var.isel(time=time_index).values
        print(f"\nAnalyzing time index {time_index}")
    else:
        data = var.values

    # Value distribution
    print("\nValue Distribution:")
    print(f"  Total elements: {data.size:,}")

    # Handle NaN values
    if np.issubdtype(data.dtype, np.floating):
        nan_mask = np.isnan(data)
        nan_count = nan_mask.sum()
        print(f"  NaN values: {nan_count:,} ({100*nan_count/data.size:.2f}%)")
        valid_mask = ~nan_mask
    else:
        valid_mask = np.ones_like(data, dtype=bool)

    # Fill values
    fill_values = []
    for attr in ['_FillValue', 'missing_value', 'fill_value']:
        if hasattr(var, attr):
            fill_val = getattr(var, attr)
            fill_values.append(fill_val)
            fill_mask = (data == fill_val)
            fill_count = fill_mask.sum()
            print(f"  {attr}: {fill_val} ({fill_count:,} occurrences, "
                  f"{100*fill_count/data.size:.2f}%)")
            valid_mask &= ~fill_mask

    # Statistics on valid data
    valid_data = data[valid_mask]
    print(f"\nValid Data Statistics:")
    print(f"  Valid values: {valid_data.size:,} ({100*valid_data.size/data.size:.2f}%)")

    if valid_data.size > 0:
        print(f"  Min: {valid_data.min():.6g}")
        print(f"  Max: {valid_data.max():.6g}")
        print(f"  Mean: {valid_data.mean():.6g}")
        print(f"  Median: {np.median(valid_data):.6g}")
        print(f"  Std dev: {valid_data.std():.6g}")

        # Value counts
        unique_vals = np.unique(valid_data)
        print(f"  Unique values: {len(unique_vals):,}")
        print(f"  Zero values: {(valid_data == 0).sum():,}")
        print(f"  Negative values: {(valid_data < 0).sum():,}")
        print(f"  Positive values: {(valid_data > 0).sum():,}")

        # Show most common values
        if len(unique_vals) < 20:
            print("\nValue counts:")
            unique, counts = np.unique(valid_data, return_counts=True)
            for val, count in zip(unique, counts):
                print(f"  {val}: {count:,}")
    else:
        print("  No valid data found!")


def main():
    parser = argparse.ArgumentParser(
        description='Diagnostic tool for NetCDF files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Analyze a specific variable
    python netcdf_diagnostic.py input.nc temperature

    # Analyze with specific time index
    python netcdf_diagnostic.py input.nc temperature -t 0

    # Show basic file information
    python netcdf_diagnostic.py input.nc
"""
    )

    parser.add_argument('file', help='Full path to the input NetCDF file')
    parser.add_argument('variable', nargs='?', help='Variable to analyze')
    parser.add_argument('-t', '--time-index', type=int, default=0,
                        help='Time index to analyze (default: 0)')

    args = parser.parse_args()

    try:
        # Check file exists
        nc_file = Path(args.file)
        if not nc_file.exists():
            raise FileNotFoundError(f"File not found: {nc_file}")

        # Open dataset
        ds = xr.open_dataset(nc_file)

        # Print basic dataset information
        print("\nDATASET INFORMATION")
        print("=" * 80)
        print(f"Filename: {nc_file.name}")
        print(f"Size: {nc_file.stat().st_size / (1024*1024):.2f} MB")
        print(f"\nDimensions:")
        for dim, size in ds.dims.items():
            print(f"  {dim}: {size:,}")

        print(f"\nVariables ({len(ds.data_vars)}):")
        for var_name, var in ds.data_vars.items():
            print(f"  {var_name}: {var.dims} {var.shape}")

        # If variable specified, analyze it
        if args.variable:
            if args.variable not in ds.data_vars:
                print(f"\nError: Variable '{args.variable}' not found!")
                print("Available variables:", list(ds.data_vars.keys()))
                return 1

            analyze_variable(ds, args.variable, args.time_index)

        ds.close()
        return 0

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
