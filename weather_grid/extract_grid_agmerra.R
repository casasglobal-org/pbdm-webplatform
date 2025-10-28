# extract_grid_agmerra.R
# Get a file similar to PUNTI_DI_TERRA.dat used for Protheus.
# Author: Luigi Ponti quartese gmail.com
# Copyright: (c) 2006 CASAS (Center for the Analysis of Sustainable Agricultural Systems, https://www.casasglobal.org/)
# SPDX-License-Identifier: GPL-3.0-or-later
# 2015-07-19
# Extract coordinates from netCDF grid
# Functionality from this script is now included in netcdf_grid_extract.py

# AgMERRA and AgCFSR Climate Forcing Datasets for Agricultural Modeling
# https://data.giss.nasa.gov/impacts/agmipcf/

get_agmerra_grid <- function(workdir="C:/Users/Luigi/maxtor/pending papers/Coffee",
							infile="AgMERRA_1981_tmin.nc4", 
							outfile="agmerra_grid_with_coords.txt") {	
	require(ncdf4)
	# Dir for reading data
	setwd(workdir)
	# Open a random NetCDF to read
	nc_tmp <- nc_open(infile)
	
	# Write header of outfile.
	cat("x", "y", "lon", "lat",
		file=outfile, sep="\t", append=TRUE)
	cat("\n", file=outfile, sep="", append=TRUE)
	
	# Loop through grid cells.
	for (x in 1:1440) {
		for (y in 1:720) {			
			# Check if current grid has data (i.e., if
			# it is land) and if it does, write to file.
			data <- ncvar_get(nc_tmp, "tmin", 
				start=c(x, y, 1), count=c(1, 1, 1))	
			# Get longitude and latitude of current grid
			# and write them to outfile wiht x and y.
			if (!(is.na(data))) {				
				lon <- ncvar_get(nc_tmp, "longitude", start=x, count=1)
				lat <- ncvar_get(nc_tmp, "latitude", start=y, count=1)		
				cat(x, y, lon, lat,
					file=outfile, sep="\t", append=TRUE)
				cat("\n", file=outfile, sep="", append=TRUE)
			}			
		}		
	}
}

get_agmerra_grid()

