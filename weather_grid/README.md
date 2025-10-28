# NetCDF Grid Information and Extraction Tools

Python tools to extract grid information and coordinates from NetCDF climate files. These tools replace the functionality of several R scripts used in the PBDM framework for extracting weather grids.

## Tools Overview

### 1. `netcdf_grid_info.py`

Extracts basic information from NetCDF files. Replaces the metadata extraction functionality from:

- `extract_grid_agmerra.R`
- `extract_grid_agera5.R`
- `extract_grid_nex-gddp.R`

**Features:**

- Displays dataset summary
- Lists variables and their attributes
- Shows coordinate information
- Provides statistical summaries
- Saves detailed information to text file

**Usage:**

```bash
python netcdf_grid_info.py -d /path/to/data -i climate_file.nc
```

### 2. `netcdf_grid_extract.py`

Extracts land grid coordinates from climate NetCDF files. Replaces the grid extraction functionality from:

- `extract_grid_agmerra.R`
- `extract_grid_agera5.R`
- `extract_grid_nex-gddp.R`

**Features:**

- Supports multiple data sources:
  - AgERA5 (Copernicus Climate Service)
  - NASA NEX-GDDP-CMIP6
  - Generic CF-compliant NetCDF files
- Identifies land points
- Extracts coordinates
- Generates GRASS GIS compatible output

**Usage:**

```bash
python netcdf_grid_extract.py -d /path/to/data -i climate_file.nc -v variable_name
```

### 3. `netcdf_grid_diagnostic.py`

Diagnostic tool for troubleshooting NetCDF files and grid extraction issues.

**Features:**

- Performs detailed analysis of specific variables
- Shows value distributions and statistics
- Identifies data quality issues (NaN, fill values)
- Helps diagnose grid extraction problems

**Usage:**

```bash
# Analyze a specific variable
python netcdf_diagnostic.py input.nc temperature

# Analyze with specific time index
python netcdf_diagnostic.py input.nc temperature -t 0
```

### 4. `grass_gis_notes.sh`

GRASS GIS commands to import extracted weather grid coordinates.

**Key Operations:**

```bash
# Create new location (if needed)
grass -c EPSG:4326 /path/to/grassdata/WGS84

# Import points from extracted grid
v.in.ascii input=extracted_grid.txt output=weather_stations \
    columns='x double precision, y double precision' \
    separator=tab skip=1

# Set region to points
g.region vect=weather_stations
```

## Installation

### Required Python Packages:

```bash
pip install xarray netCDF4 numpy
```

Or using conda:

```bash
conda install -c conda-forge xarray netCDF4 numpy
```

### Requires GRASS GIS Installation

For macOS using Homebrew:

```bash
brew install grass
```

## Workflow

1. **Extract Grid Information:**

   ```bash
   python netcdf_grid_info.py -d /data -i climate.nc
   ```

2. **Extract Grid Coordinates:**

   ```bash
   python netcdf_grid_extract.py -d /data -i climate.nc -v temperature
   ```

3. **Import to GRASS GIS:**

   ```bash
   # Follow commands in grass_gis_notes.sh
   ```

## File Format Support

### Input Formats

- AgERA5 NetCDF files
- NASA NEX-GDDP-CMIP6 NetCDF files
- Any CF-compliant NetCDF file with lat/lon coordinates

### Output Formats

- Text files with grid information (`*.info.txt`)
- Tab-separated coordinate files for GRASS GIS import
- Variable statistics and summaries

## Migration from R Scripts

These Python tools replace the following R scripts:

- `extract_grid_agmerra.R`: For AgMERRA climate data
- `extract_grid_agera5.R`: For AgERA5 climate data
- `extract_grid_nex-gddp.R`: For NASA NEX-GDDP projections

Benefits of Python implementation:

- Faster processing
- Better memory management
- Unified interface for different data sources
- Direct integration with GRASS GIS workflow

## Additional Resources

- [AgERA5 Documentation](https://cds.climate.copernicus.eu/cdsapp#!/dataset/sis-agrometeorological-indicators)
- [NASA NEX-GDDP-CMIP6](https://www.nasa.gov/nex/gddp)
- [GRASS GIS Documentation](https://grass.osgeo.org/documentation/)
- [CF Conventions](http://cfconventions.org/)

## License

GPL-3.0-or-later

## Authors

- Luigi Ponti (ENEA/CASAS Global)
- CASAS Global Development Team
