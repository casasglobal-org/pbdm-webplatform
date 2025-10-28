"""
Python script to extract basic information from a NetCDF file.
Based on first ~124 lines of extract_grid_agera5.R

Author: Luigi Ponti quartese gmail.com
Copyright: (c) 2025 CASAS (Center for the Analysis of Sustainable Agricultural
    Systems, https://www.casasglobal.org/)
SPDX-License-Identifier: GPL-3.0-or-later
"""

import xarray as xr
import numpy as np
from pathlib import Path
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description='Extract and analyze information from NetCDF files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Process a NetCDF file in the current directory
    python netcdf_grid_info.py --workdir . --infile data.nc

    # Process a NetCDF file in a specific directory
    python netcdf_grid_info.py --workdir /path/to/data --infile climate.nc

Notes:
    - The script will create a *.info.txt file with detailed information
    - Interactive mode allows selecting specific variables to analyze
    - Large datasets will prompt before loading into memory
    """)

    parser.add_argument('-d', '--workdir', 
                        type=str, 
                        required=True,
                        help='Working directory containing the NetCDF file')

    parser.add_argument('-i', '--infile', 
                        type=str, 
                        required=True,
                        help='Input NetCDF filename (e.g., data.nc)')

    return parser.parse_args()


def main():
    args = parse_args()

    # Convert to Path objects
    workdir = Path(args.workdir)
    infile = Path(args.infile)

    # Change to working directory
    workdir.resolve().absolute()
    if not workdir.exists():
        raise FileNotFoundError(f"Working directory not found: {workdir}")

    # Full path to input file
    netcdf_file = workdir / infile
    if not netcdf_file.exists():
        raise FileNotFoundError(f"Input file not found: {netcdf_file}")

    # Open the NetCDF file with xarray
    ds = xr.open_dataset(netcdf_file)

    # Print dataset information to a text file
    print(f"{netcdf_file.stem}\n" + "=" * 80 + "\n")
    output_file = f"{workdir / netcdf_file.stem}.info.txt"
    with open(output_file, 'w') as f:
        # Redirect print output to file
        f.write(str(ds))
        f.write("\n\n")
        f.write("=" * 80 + "\n")
        f.write("Detailed Information:\n")
        f.write("=" * 80 + "\n\n")

        # Variables
        f.write(f"Data Variables ({len(ds.data_vars)}):\n")
        for var_name in ds.data_vars:
            var = ds[var_name]
            f.write(f"\n  {var_name}:\n")
            f.write(f"    dtype: {var.dtype}\n")
            f.write(f"    dimensions: {var.dims}\n")
            f.write(f"    shape: {var.shape}\n")
            f.write(f"    attributes:\n")
            for attr, value in var.attrs.items():
                f.write(f"      {attr}: {value}\n")

        # Coordinates/Dimensions
        f.write(f"\n\nCoordinates ({len(ds.coords)}):\n")
        for coord_name in ds.coords:
            coord = ds[coord_name]
            f.write(f"\n  {coord_name}:\n")
            f.write(f"    size: {coord.size}\n")
            f.write(f"    dtype: {coord.dtype}\n")
            f.write(f"    attributes:\n")
            for attr, value in coord.attrs.items():
                f.write(f"      {attr}: {value}\n")

        # Global attributes
        f.write(f"\n\nGlobal Attributes ({len(ds.attrs)}):\n")
        for attr, value in ds.attrs.items():
            f.write(f"  {attr}: {value}\n")

    print(f"Dataset information saved to {output_file}")

    # Display basic dataset information
    print("\n" + "=" * 80)
    print("DATASET SUMMARY")
    print("=" * 80)
    print(ds)

    # Get summary statistics
    num_vars = len(ds.data_vars)
    num_coords = len(ds.coords)
    num_attrs = len(ds.attrs)
    print(f"\nThe file has {num_vars} data variables, {num_coords} coordinates and {num_attrs} global attributes")

    # Get list of variable names
    var_names = list(ds.data_vars.keys())
    print(f"\nData variable names: {var_names}")

    # Get list of variable names
    var_names = list(ds.data_vars.keys())
    print(f"\nData variable names: {var_names}")

    # Interactive variable selection
    print(f"\n" + "=" * 80)
    print("VARIABLE SELECTION")
    print("=" * 80)

    if len(ds.data_vars) == 0:
        print("\nNo data variables found in the dataset.")
    else:
        # Display available variables
        var_list = list(ds.data_vars.keys())
        print(f"\nAvailable data variables ({len(var_list)}):")
        for i, var_name in enumerate(var_list, 1):
            var_info = ds[var_name]
            print(f"  {i}. {var_name}")
            print(f"     Dimensions: {var_info.dims}, Shape: {var_info.shape}")
            if 'long_name' in var_info.attrs:
                print(f"     Description: {var_info.attrs['long_name']}")

        # Prompt user for selection
        print("\nSelect variable(s) to analyze:")
        print("  - Enter a number (e.g., '1')")
        print("  - Enter multiple numbers separated by commas (e.g., '1,2,3')")
        print("  - Enter 'all' to analyze all variables")
        print("  - Press Enter to skip variable analysis")

        user_input = input("\nYour selection: ").strip()

        # Parse user input
        selected_vars = []
        if user_input.lower() == 'all':
            selected_vars = var_list
        elif user_input:
            try:
                indices = [int(x.strip()) for x in user_input.split(',')]
                selected_vars = [var_list[i-1] for i in indices if 1 <= i <= len(var_list)]
            except (ValueError, IndexError):
                print("\nInvalid input. Skipping variable analysis.")

        # Process selected variables
        for var_name in selected_vars:
            var_data = ds[var_name]

            print(f"\n" + "=" * 80)
            print(f"{var_name.upper()} - Variable Details")
            print("=" * 80)

            # Display attributes
            print(f"\nAttributes:")
            if var_data.attrs:
                for attr, value in var_data.attrs.items():
                    print(f"  {attr}: {value}")
            else:
                print("  (No attributes)")

            # Display dimension and shape information
            print(f"\nDimensions: {var_data.dims}")
            print(f"Shape: {var_data.shape}")
            print(f"Data type: {var_data.dtype}")
            print(f"Size: {var_data.size:,} elements")

            # Ask if user wants to load data (for large datasets)
            data_size_mb = var_data.nbytes / (1024 * 1024)
            print(f"Estimated memory: {data_size_mb:.2f} MB")

            if data_size_mb > 100:  # Warn for large datasets
                load_data = input(f"\nThis is a large dataset. Load into memory? (y/n): ").strip().lower()
                if load_data != 'y':
                    print("Skipping data loading for this variable.")
                    continue

            # Load data into memory
            print("\nLoading data into memory...")
            try:
                data_array = var_data.values

                # Calculate statistics (excluding fill/missing values)
                fill_value = var_data.attrs.get('_FillValue', None)
                missing_value = var_data.attrs.get('missing_value', None)

                # Create mask for valid data - start with all True
                valid_mask = np.ones(data_array.shape, dtype=bool)

                # First, exclude NaN values
                if np.issubdtype(data_array.dtype, np.floating):
                    valid_mask &= ~np.isnan(data_array)

                # Then exclude fill values (with type-safe comparison)
                if fill_value is not None:
                    try:
                        # Convert fill_value to same dtype as data for comparison
                        fill_val_converted = np.array(fill_value).astype(data_array.dtype)
                        valid_mask &= (data_array != fill_val_converted)
                    except (ValueError, TypeError):
                        print(f"  Warning: Could not compare with _FillValue: {fill_value}")

                # Exclude missing values if different from fill value
                if missing_value is not None and missing_value != fill_value:
                    try:
                        missing_val_converted = np.array(missing_value).astype(data_array.dtype)
                        valid_mask &= (data_array != missing_val_converted)
                    except (ValueError, TypeError):
                        print(f"  Warning: Could not compare with missing_value: {missing_value}")

                valid_data = data_array[valid_mask]

                # Diagnostic information
                print(f"\nData filtering diagnostics:")
                print(f"  Total elements: {data_array.size:,}")
                print(f"  Data type: {data_array.dtype}")
                print(f"  Data range: [{np.nanmin(data_array):.4f}, {np.nanmax(data_array):.4f}]")
                if np.issubdtype(data_array.dtype, np.floating):
                    nan_count = np.isnan(data_array).sum()
                    print(f"  NaN values: {nan_count:,} ({100*nan_count/data_array.size:.2f}%)")
                if fill_value is not None:
                    print(f"  _FillValue: {fill_value} (dtype: {type(fill_value).__name__})")
                    fill_count = (data_array == np.array(fill_value).astype(data_array.dtype)).sum()
                    print(f"  Fill value matches: {fill_count:,}")
                if missing_value is not None:
                    print(f"  missing_value: {missing_value} (dtype: {type(missing_value).__name__})")
                    if missing_value != fill_value:
                        miss_count = (data_array == np.array(missing_value).astype(data_array.dtype)).sum()
                        print(f"  Missing value matches: {miss_count:,}")

                if len(valid_data) > 0:
                    print(f"\nData statistics (excluding fill/missing values):")
                    print(f"  Valid values: {len(valid_data):,} / {data_array.size:,} ({100*len(valid_data)/data_array.size:.1f}%)")
                    print(f"  Min: {valid_data.min():.4f}")
                    print(f"  Max: {valid_data.max():.4f}")
                    print(f"  Mean: {valid_data.mean():.4f}")
                    print(f"  Median: {np.median(valid_data):.4f}")
                    print(f"  Std: {valid_data.std():.4f}")

                    # Percentiles
                    percentiles = np.percentile(valid_data, [25, 50, 75])
                    print(f"  25th percentile: {percentiles[0]:.4f}")
                    print(f"  50th percentile: {percentiles[1]:.4f}")
                    print(f"  75th percentile: {percentiles[2]:.4f}")

                    # Additional useful statistics
                    print(f"\nAdditional statistics:")
                    print(f"  Unique values: {len(np.unique(valid_data)):,}")
                    print(f"  Zero values: {(valid_data == 0).sum():,}")
                    print(f"  Negative values: {(valid_data < 0).sum():,}")
                    print(f"  Positive values: {(valid_data > 0).sum():,}")
                else:
                    print("\n⚠ WARNING: No valid data found!")
                    print("  All values appear to be fill/missing values or NaN.")
                    print("\n  Troubleshooting suggestions:")
                    print("  1. Check if the variable has data for your region/time")
                    print("  2. Verify the fill value is correct")
                    print("  3. Try using xarray's built-in masking: var_data.where(var_data != fill_value)")

                    # Try alternative approach with xarray
                    print("\n  Attempting alternative data extraction with xarray...")
                    try:
                        # Use xarray's where to mask invalid values
                        masked_data = var_data.where(var_data != fill_value) if fill_value else var_data
                        masked_data = masked_data.where(var_data != missing_value) if missing_value else masked_data

                        # Get valid values
                        alt_valid = masked_data.values[~np.isnan(masked_data.values)]

                        if len(alt_valid) > 0:
                            print(f"  ✓ Alternative method found {len(alt_valid):,} valid values")
                            print(f"    Range: [{alt_valid.min():.4f}, {alt_valid.max():.4f}]")
                            print(f"    Mean: {alt_valid.mean():.4f}")
                        else:
                            print("  ✗ Alternative method also found no valid data")
                    except Exception as e:
                        print(f"  ✗ Alternative method failed: {e}")

            except Exception as e:
                print(f"\nError loading data: {e}")
                continue

    # Retrieve coordinate information
    print(f"\n" + "=" * 80)
    print("Coordinate Information")
    print("=" * 80)

    if 'lat' in ds.coords:
        lat = ds['lat']
        latsize = lat.size
        print(f"\nLatitude:")
        print(f"  Size: {latsize}")
        print(f"  Range: {lat.values.min():.2f} to {lat.values.max():.2f}")
        print(f"  Units: {lat.attrs.get('units', 'N/A')}")

    if 'lon' in ds.coords:
        lon = ds['lon']
        lonsize = lon.size
        print(f"\nLongitude:")
        print(f"  Size: {lonsize}")
        print(f"  Range: {lon.values.min():.2f} to {lon.values.max():.2f}")
        print(f"  Units: {lon.attrs.get('units', 'N/A')}")

        # Get last longitude value (equivalent to R's start=lonsize, count=1)
        last_longitude = lon.values[-1]
        print(f"  Last value: {last_longitude:.2f}")

    if 'time' in ds.coords:
        time = ds['time']
        print(f"\nTime:")
        print(f"  Size: {time.size}")
        print(f"  Units: {time.attrs.get('units', 'N/A')}")
        print(f"  Calendar: {time.attrs.get('calendar', 'N/A')}")
        print(f"  Range: {time.values[0]} to {time.values[-1]}")

        # Convert to datetime if possible
        try:
            time_datetime = xr.decode_cf(ds)['time']
            print(f"  Date range: {time_datetime.values[0]} to {time_datetime.values[-1]}")
        except:
            print("  (Could not decode to datetime)")

    # Close the dataset (xarray handles this automatically, but explicit is good)
    ds.close()
    print("\n" + "=" * 80)
    print("Dataset closed.")
    print("=" * 80)

    # Date conversion example
    print("\n" + "=" * 80)
    print("Date Conversion Examples")
    print("=" * 80)

    # Example 1: days since 1980-01-01
    days_since = 10071
    origin_date = np.datetime64('1980-01-01')
    calculated_date = origin_date + np.timedelta64(days_since, 'D')
    print(f"\n{days_since} days since 1980-01-01 = {calculated_date}")

    # Example 2: days since 1900-01-01 (matching NetCDF time units)
    days_since_1900 = 43070  # Example: corresponds to 2017-12-01
    origin_1900 = np.datetime64('1900-01-01')
    date_1900 = origin_1900 + np.timedelta64(days_since_1900, 'D')
    print(f"{days_since_1900} days since 1900-01-01 = {date_1900}")

    print("\n" + "=" * 80)
    print("Processing complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
