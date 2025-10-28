#!/usr/bin/env python3
"""
Extract land grid coordinates from climate netCDF files using xarray.
Supports multiple data sources: AgERA5, NASA NEX-GDDP-CMIP6, and other
CF-compliant files.

This universal version automatically detects file structure and adapts to
different naming conventions, dimension orders, and metadata formats.

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
from datetime import datetime


def detect_file_type(ds):
    """
    Detect the type of climate data file.

    Parameters:
    -----------
    ds : xarray.Dataset
        The opened dataset

    Returns:
    --------
    str : File type identifier ('agera5', 'nex-gddp', 'generic')
    """
    # Check global attributes for identifiers
    attrs_str = ' '.join([str(v).lower() for v in ds.attrs.values()])

    if ('agera5' in attrs_str or 'c3s' in attrs_str
            or 'copernicus' in attrs_str):
        return 'agera5'
    elif ('nex-gddp' in attrs_str or 'cmip6' in attrs_str
            or 'nasa' in attrs_str):
        return 'nex-gddp'
    else:
        return 'generic'


def find_dimension_names(ds, var):
    """
    Find latitude and longitude dimension names in dataset.
    Handles various naming conventions (lat/latitude, lon/longitude, etc.)

    Parameters:
    -----------
    ds : xarray.Dataset
        The dataset
    var : xarray.DataArray
        The variable to analyze

    Returns:
    --------
    tuple : (lon_dim, lat_dim, time_dim) or raises ValueError if not found
    """
    dims = var.dims

    # Common patterns for dimension names
    lon_patterns = ['lon', 'longitude', 'x', 'xc']
    lat_patterns = ['lat', 'latitude', 'y', 'yc']
    time_patterns = ['time', 't', 'date']

    lon_dim = None
    lat_dim = None
    time_dim = None

    # Search for longitude dimension
    for dim in dims:
        dim_lower = dim.lower()
        if any(pattern in dim_lower for pattern in lon_patterns):
            lon_dim = dim
            break

    # Search for latitude dimension
    for dim in dims:
        dim_lower = dim.lower()
        if any(pattern in dim_lower for pattern in lat_patterns):
            lat_dim = dim
            break

    # Search for time dimension
    for dim in dims:
        dim_lower = dim.lower()
        if any(pattern in dim_lower for pattern in time_patterns):
            time_dim = dim
            break

    # If not found by name, try by coordinate variable attributes
    if lon_dim is None or lat_dim is None:
        for coord_name in ds.coords:
            if coord_name in dims:
                coord = ds[coord_name]
                if hasattr(coord, 'axis'):
                    axis = coord.axis.lower()
                    if axis == 'x' and lon_dim is None:
                        lon_dim = coord_name
                    elif axis == 'y' and lat_dim is None:
                        lat_dim = coord_name
                    elif axis == 't' and time_dim is None:
                        time_dim = coord_name

                # Check standard_name attribute
                if hasattr(coord, 'standard_name'):
                    std_name = coord.standard_name.lower()
                    if 'longitude' in std_name and lon_dim is None:
                        lon_dim = coord_name
                    elif 'latitude' in std_name and lat_dim is None:
                        lat_dim = coord_name
                    elif 'time' in std_name and time_dim is None:
                        time_dim = coord_name

    if lon_dim is None or lat_dim is None:
        raise ValueError(f"Could not identify lon/lat dimensions. "
                         f"Available dimensions: {dims}")

    return lon_dim, lat_dim, time_dim


def get_fill_values(var):
    """
    Get all possible fill/missing value indicators from variable.

    Parameters:
    -----------
    var : xarray.DataArray
        The variable

    Returns:
    --------
    list : List of fill values to check
    """
    fill_values = []

    # Standard fill value attributes
    for attr_name in ['_FillValue', 'missing_value',
                      'fill_value', 'FillValue']:
        if hasattr(var, attr_name):
            fill_val = getattr(var, attr_name)
            if fill_val is not None:
                fill_values.append(fill_val)

    # NetCDF4 encoding fill value
    if hasattr(var, 'encoding') and '_FillValue' in var.encoding:
        fill_values.append(var.encoding['_FillValue'])

    return list(set(fill_values))  # Remove duplicates


def extract_land_grid(workdir='/Users/user/tmp',
                      infile="example.nc",
                      variable="pr",
                      outfile="land_grid.txt",
                      time_index=0,
                      auto_detect=True,
                      verbose=True):
    """
    Extract land grid coordinates from climate netCDF file using xarray.

    Universal version supporting multiple data formats:
    - AgERA5 (Copernicus Climate Service)
    - NASA NEX-GDDP-CMIP6 (NASA Earth Exchange)
    - Generic CF-compliant NetCDF files

    Parameters:
    -----------
    workdir : str
        Working directory path
    infile : str
        Input netCDF filename
    variable : str
        Variable name to check for land vs. water
    outfile : str
        Output text file for grid coordinates
    time_index : int or str
        Time slice to use for land/water determination.
        Can be an integer index or 'first', 'last', 'middle'
    auto_detect : bool
        Automatically detect file type and adapt processing
    verbose : bool
        Print progress messages

    Returns:
    --------
    int : Number of land cells found
    """
    # Setup paths
    workdir = Path(workdir)
    infile_path = workdir / infile
    outfile_path = workdir / outfile

    if not infile_path.exists():
        raise FileNotFoundError(f"Input file not found: {infile_path}")

    if verbose:
        print("=" * 80)
        print("UNIVERSAL LAND GRID EXTRACTION")
        print("=" * 80)
        print(f"Input file:  {infile_path}")
        print(f"Variable:    {variable}")
        print(f"Output file: {outfile_path}")
        print(f"Time index:  {time_index}")

    try:
        # Open dataset with xarray
        ds = xr.open_dataset(infile_path)

        # Detect file type
        if auto_detect:
            file_type = detect_file_type(ds)
            if verbose:
                print(f"Detected file type: {file_type.upper()}")
        else:
            file_type = 'generic'

        # Print dataset information
        if verbose:
            print(f"\nDataset overview:")
            if hasattr(ds, 'title'):
                print(f"  Title: {ds.title}")
            if hasattr(ds, 'source'):
                print(f"  Source: {ds.source}")
            if hasattr(ds, 'institution'):
                print(f"  Institution: {ds.institution}")
            print(f"  Dimensions: {dict(ds.dims)}")

        # Verify variable exists
        if variable not in ds.data_vars:
            available_vars = list(ds.data_vars.keys())
            raise ValueError(
                f"Variable '{variable}' not found.\n"
                f"Available variables: {available_vars}\n"
                f"Tip: Use netcdf_extractor_xarray.py "
                f"to explore the file first."
            )

        # Get variable
        var = ds[variable]

        if verbose:
            print(f"\nVariable '{variable}':")
            print(f"  Dimensions: {var.dims}")
            print(f"  Shape: {var.shape}")
            print(f"  Data type: {var.dtype}")
            if hasattr(var, 'long_name'):
                print(f"  Long name: {var.long_name}")
            if hasattr(var, 'units'):
                print(f"  Units: {var.units}")

        # Find coordinate dimensions
        try:
            lon_dim, lat_dim, time_dim = find_dimension_names(ds, var)

            if verbose:
                print(f"\nIdentified dimensions:")
                print(f"  Longitude: {lon_dim}")
                print(f"  Latitude:  {lat_dim}")
                if time_dim:
                    print(f"  Time:      {time_dim}")
        except ValueError as e:
            raise ValueError(
                f"{e}\n"
                f"This file may not be CF-compliant or "
                f"uses non-standard dimension names.\n"
                f"Available dimensions: {list(ds.dims.keys())}"
            )

        # Get coordinates
        longitude = ds[lon_dim].values
        latitude = ds[lat_dim].values

        if verbose:
            print(f"\nCoordinate ranges:")
            print(f"  {lon_dim}: {len(longitude):,} "
                  f"points, range [{longitude.min():.4f}, "
                  f"{longitude.max():.4f}]")
            print(f"  {lat_dim}: {len(latitude):,} "
                  f"points, range [{latitude.min():.4f}, "
                  f"{latitude.max():.4f}]")
            if time_dim:
                time_size = len(ds[time_dim])
                print(f"  {time_dim}: {time_size:,} points")

        # Handle time selection
        if time_dim:
            time_size = len(ds[time_dim])

            # Convert string time_index to integer
            if isinstance(time_index, str):
                time_index_str = time_index.lower()
                if time_index_str == 'first':
                    time_index = 0
                elif time_index_str == 'last':
                    time_index = time_size - 1
                elif time_index_str == 'middle':
                    time_index = time_size // 2
                else:
                    raise ValueError(f"Invalid time_index string: "
                                     f"{time_index}. Use 'first', "
                                     f"'last', or 'middle'")

            # Validate time index
            if time_index < 0 or time_index >= time_size:
                raise ValueError(
                    f"Time index {time_index} out of range "
                    f"[0, {time_size-1}]\n"
                    f"The file has {time_size} time steps."
                )

            if verbose:
                print(f"\nSelecting time index {time_index} "
                      f"(of {time_size})...")
                # Try to show the actual date if available
                try:
                    time_val = ds[time_dim].isel({time_dim: time_index})
                    print(f"  Time value: {time_val.values}")
                except (KeyError, AttributeError) as e:
                    if verbose:
                        print(f"  Warning: Could not get time value: {str(e)}")
                        print("  This is not critical, \
                              continuing extraction...")
                    pass

            data_slice = var.isel({time_dim: time_index})
        else:
            if verbose:
                print(f"\nNo time dimension found, using full data array...")
            data_slice = var

        if verbose:
            print(f"  Data slice shape: {data_slice.shape}")

        # Get fill values
        fill_values = get_fill_values(data_slice)

        if verbose:
            if fill_values:
                print(f"  Fill/missing values: {fill_values}")
            else:
                print("  No explicit fill value found \
                      (will check for NaN only)")

        # Load data into memory
        if verbose:
            mem_size = data_slice.nbytes / (1024**2)
            print(f"\nLoading data into memory ({mem_size:.2f} MB)...")

        data_values = data_slice.values

        # Create mask for valid (land) cells
        valid_mask = np.ones(data_values.shape, dtype=bool)

        # Exclude NaN values
        if np.issubdtype(data_values.dtype, np.floating):
            nan_mask = np.isnan(data_values)
            valid_mask &= ~nan_mask
            if verbose:
                nan_count = nan_mask.sum()
                print(f"  NaN values: {nan_count:,} "
                      f"({100*nan_count/data_values.size:.2f}%)")

        # Exclude fill values
        for fill_val in fill_values:
            try:
                fill_val_converted = np.array(fill_val).astype(data_values.dtype)
                fill_mask = (data_values == fill_val_converted)
                valid_mask &= ~fill_mask
                if verbose:
                    fill_count = fill_mask.sum()
                    print(f"  Values equal to {fill_val}: {fill_count:,} "
                          f"({100*fill_count/data_values.size:.2f}%)")
            except (ValueError, TypeError) as e:
                if verbose:
                    print(f"Warning: Could not compare "
                          f"with fill value {fill_val}: {e}")

        land_count = valid_mask.sum()

        if verbose:
            print(f"\n  Valid (land) cells: "
                  f"{land_count:,} / {valid_mask.size:,} "
                  f"({100*land_count/valid_mask.size:.2f}%)")

        # Warn if very few or no land cells
        if land_count == 0:
            print("\n⚠ WARNING: No land cells found!")
            print("  Possible reasons:")
            print("  - The entire dataset is over ocean")
            print("  - Wrong variable selected")
            print("  - Wrong time index")
            print("  - All values are fill/missing values")
            print("\n  Suggestion: Run netcdf_diagnostic.py to investigate")
        elif land_count < valid_mask.size * 0.01:
            print(f"\n⚠ WARNING: Very few land cells found "
                  f"({land_count:,}, {100*land_count/valid_mask.size:.2f}%)")
            print("  This might be normal for \
                  ocean-dominated regions or coarse grids.")

        # Determine dimension order for indexing
        dim_order = data_slice.dims

        # Find which axis corresponds to lat/lon
        lat_axis = dim_order.index(lat_dim)
        lon_axis = dim_order.index(lon_dim)

        if verbose:
            print(f"\n  Array dimension order: {dim_order}")
            print(f"  Longitude axis: {lon_axis}, Latitude axis: {lat_axis}")

        # Write header
        with open(outfile_path, 'w') as f:
            f.write("x\ty\tlon\tlat\n")

        if verbose:
            print("\nExtracting land grid cells...")

        # Get indices of valid cells
        valid_indices = np.where(valid_mask)

        if verbose and land_count > 0:
            print(f"  Processing {land_count:,} land cells...")

        # Write land cells
        with open(outfile_path, 'a') as f:
            for i in range(land_count):
                if verbose and i % 100000 == 0 and i > 0:
                    print(f"  Written {i:,} / "
                          f"{land_count:,} cells ({100*i/land_count:.1f}%)...")

                # Get array indices based on dimension order
                if len(valid_indices) == 2:
                    idx0 = valid_indices[0][i]
                    idx1 = valid_indices[1][i]

                    # Map to lon/lat based on dimension order
                    if lon_axis == 0:
                        lon_idx = idx0
                        lat_idx = idx1
                    else:
                        lon_idx = idx1
                        lat_idx = idx0
                else:
                    raise ValueError(f"Unexpected number of dimensions: "
                                     f"{len(valid_indices)}")

                # Write to file with higher precision for coordinates
                f.write(f"{lon_idx+1}\t{lat_idx+1}\t"
                        f"{longitude[lon_idx]:.6f}\t"
                        f"{latitude[lat_idx]:.6f}\n")

        ds.close()

        if verbose:
            print(f"\n" + "=" * 80)
            print(f"EXTRACTION COMPLETE")
            print("=" * 80)
            print(f"Land cells found: {land_count:,}")
            if land_count > 0:
                print(f"Output saved to:  {outfile_path}")
                print(f"File size:        "
                      f"{outfile_path.stat().st_size / 1024:.2f} KB")

                # Show spatial coverage
                if land_count > 0:
                    land_lons = longitude[valid_indices[lon_axis]]
                    land_lats = latitude[valid_indices[lat_axis]]
                    print(f"\nSpatial coverage:")
                    print(f"  Longitude: [{land_lons.min():.4f}, "
                          f"{land_lons.max():.4f}]")
                    print(f"  Latitude:  [{land_lats.min():.4f}, "
                          f"{land_lats.max():.4f}]")
            else:
                print("No output file created (no land cells found)")

        return land_count

    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        if verbose:
            import traceback
            print("\nFull traceback:")
            traceback.print_exc()
        raise


# Backward compatibility: keep old function name
def get_agera5_grid_land_xr(*args, **kwargs):
    """
    Backward compatibility wrapper.
    This function name is deprecated - use extract_land_grid() instead.
    """
    return extract_land_grid(*args, **kwargs)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Universal land grid extraction \
            from climate NetCDF files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported Data Sources:
  • AgERA5 (Copernicus Climate Service)
  • NASA NEX-GDDP-CMIP6 (NASA Earth Exchange Global Daily Downscaled
    Projections)
  • Any CF-compliant NetCDF file with lat/lon coordinates

Examples:
  # AgERA5 data
  python netcdf_grid_extract.py -i agera5_file.nc -v Solar_Radiation_Flux

  # NASA NEX-GDDP-CMIP6 data
  python netcdf_grid_extract.py -i tas_day_MPI-ESM1-2-HR_ssp585.nc -v tas

  # Use different time selections
  python netcdf_grid_extract.py -t first    # First time step
  python netcdf_grid_extract.py -t last     # Last time step
  python netcdf_grid_extract.py -t middle   # Middle time step
  python netcdf_grid_extract.py -t 15       # Specific index

  # Quiet mode for batch processing
  python netcdf_grid_extract.py -q

  # Disable auto-detection (faster for known file types)
  python netcdf_grid_extract.py --no-auto-detect
        """
    )

    parser.add_argument('-d', '--workdir',
                        default='.',
                        help='Working directory (default: current directory)')

    parser.add_argument('-i', '--infile',
                        default='example.nc',
                        help='Input netCDF filename')

    parser.add_argument('-v', '--variable',
                        default='Solar_Radiation_Flux',
                        help='Variable name to check')

    parser.add_argument('-o', '--outfile',
                        default='extracted_grid.txt',
                        help='Output text file for grid coordinates')

    parser.add_argument('-t', '--time-index',
                        default=0,
                        help='Time slice to use: integer index, \
                            "first", "last", or "middle" (default: 0)')

    parser.add_argument('--no-auto-detect',
                        action='store_true',
                        help='Disable automatic file type detection (faster)')

    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='Suppress progress messages')

    args = parser.parse_args()

    # Convert time_index to int if possible
    time_index = args.time_index
    try:
        time_index = int(time_index)
    except ValueError:
        # Keep as string for 'first', 'last', 'middle'
        pass

    try:
        start_time = datetime.now()

        land_count = extract_land_grid(
            workdir=args.workdir,
            infile=args.infile,
            variable=args.variable,
            outfile=args.outfile,
            time_index=time_index,
            auto_detect=not args.no_auto_detect,
            verbose=not args.quiet
        )

        elapsed = (datetime.now() - start_time).total_seconds()

        if not args.quiet:
            print(f"\nProcessing time: {elapsed:.2f} seconds")
            if land_count > 0:
                print(f"✓ Success! Extracted {land_count:,} land cells.")
            else:
                print(f"⚠ Warning: No land cells found. Check your data.")

        return 0 if land_count > 0 else 1

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if not args.quiet:
            print("\nTroubleshooting tips:")
            print("  1. Verify the file exists and is accessible")
            print("  2. Check variable name with: ncdump -h file.nc \
                  or netcdf_grid_info.py")
            print("  3. Run: python netcdf_extractor_xarray.py -i file.nc")
            print("  4. Run diagnostics: python netcdf_diagnostic.py file.nc variable")
        return 1


if __name__ == "__main__":
    sys.exit(main())
