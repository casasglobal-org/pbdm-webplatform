
# extract_grid_agera5.R
# Author: Luigi Ponti quartese gmail.com
# Copyright: (c) 2006 CASAS (Center for the Analysis of Sustainable Agricultural Systems, https://www.casasglobal.org/)
# SPDX-License-Identifier: GPL-3.0-or-later
# 2019-11-04
# Extract coordinates from netCDF grid
# Functionality from this script is now included in netcdf_grid_extract.py

# AgERA5 data for agriculture from hourly ECMWF ERA5 data at surface level
# http://global-agriculture.copernicus-climate.eu/datastream2/AgERA5/

# For moving stuff around my giotto home dir
mv -iv *rcp85*.nc MPI-ESM-LR_rcp85/
mv -iv *historical*.nc MPI-ESM-LR_historical/

# in R Studio

library(ncdf4)

setwd("/home/luigi/LUIGI/agera5")

ncin <- nc_open("Solar-Radiation-Flux_C3S-glob-agric_AgERA5_daily_20171201-20171231_final-v1.0.nc")

# https://www.r-bloggers.com/a-netcdf-4-in-r-cheatsheet/
# Save the print(nc) dump to a text file (same name as the nc file with a txt extension)
sink(paste0("Solar-Radiation-Flux_C3S-glob-agric_AgERA5_daily_20171201-20171231_final-v1.0.nc", ".txt"))
print(ncin)
sink()

File Solar-Radiation-Flux_C3S-glob-agric_AgERA5_daily_20171201-20171231_final-v1.0.nc (NC_FORMAT_NETCDF4):

     1 variables (excluding dimension variables):
        float Solar_Radiation_Flux[lon,lat,time]   (Chunking: [3600,18,1])  (Compression: shuffle,level 4)
            long_name: Surface solar radiation downwards (00-00LT)
            units: J m-2 d-1
            _FillValue: -9999
            missing_value: -9999
            temporal_aggregation: Sum 00-00LT

     3 dimensions:
        time  Size:31   *** is unlimited ***
            standard_name: time
            long_name: time
            units: days since 1900-01-01
            calendar: proleptic_gregorian
            axis: T
        lon  Size:3600
            long_name: "longitude"
            units: "degrees_east"
            axis: X
        lat  Size:1801
            long_name: "latitude"
            units: "degrees_north"
            axis: Y

    4 global attributes: [...]


# Get a list of the NetCDF's R attributes:
attributes(ncin)$names

 [1] "filename"    "writable"    "id"          "safemode"    "format"     
 [6] "is_GMT"      "groups"      "fqgn2Rindex" "ndims"       "natts"      
[11] "dim"         "unlimdimid"  "nvars"       "var"        

print(paste("The file has",ncin$nvars,"variables,",ncin$ndims,"dimensions and",ncin$natts,"NetCDF attributes"))

[1] "The file has 1 variables, 3 dimensions and 4 NetCDF attributes"

# Get a list of the nc variable names.
attributes(ncin$var)$names
[1] "Solar_Radiation_Flux"

# Take a look at the variable's nc attributes (units etc).
ncatt_get(ncin, attributes(ncin$var)$names[1])
# or
ncatt_get(ncin, "Solar_Radiation_Flux")

$long_name
[1] "Surface solar radiation downwards (00-00LT)"

$units
[1] "J m-2 d-1"

$`_FillValue`
[1] -9999

$missing_value
[1] -9999

$temporal_aggregation
[1] "Sum 00-00LT"


# Retrieve a matrix of the data using the ncvar_get function:
solrad <- ncvar_get(ncin, "Solar_Radiation_Flux")

# Print the data's dimensions
dim(solrad)

[1] 3600 1801   31

# Retrieve the latitude and longitude values.
> attributes(ncin$dim$lat)$names
 [1] "name"          "len"           "unlim"         "group_index"  
 [5] "group_id"      "id"            "dimvarid"      "units"        
 [9] "vals"          "create_dimvar"

latsize <- ncin$dim$lat$len
latsize
[1] 1801

lonsize <- ncin$dim$lon$len
lonsize
[1] 3600

longitude <- ncvar_get(ncin, "lon", start=lonsize, count=1)


# Close after you are done
nc_close(ncin)

# Not sure the following is useful (from screwworm 2)
#https://stat.ethz.ch/R-manual/R-devel/library/base/html/as.Date.html
date <- as.Date(10071, origin = "1980-01-01")
## date given as number of days since 1900-01-01 (a date in 1989)
cat(format(date, format="%m\t%d\t%Y"))


# Function to get coordinates of grid cells with no water (i.e., land).
# Note that both AgMERRA/AgCFSR and AgERA5 have no data for oceans.
# Worked OK but it may be appropriate to load the whole netcdf file 
# to a data frame once and then extract data (lon,lat pairs) from there.
get_agera5_grid <- function(workdir="/home/luigi/LUIGI/agera5", infile="Solar-Radiation-Flux_C3S-glob-agric_AgERA5_daily_20171201-20171231_final-v1.0.nc", variable="Solar_Radiation_Flux", outfile="agera5_grid.txt") {
	require(ncdf4)
	# Dir for reading data
	setwd(workdir)
	# open netCDF
	nc_tmp <- nc_open(infile)	
	# Print header line
	cat("x", "\t", "y", "\t", "lon", "\t", "lat", "\n",
		file=outfile, sep="")
	# Get geographic dimensions
	lonsize <- nc_tmp$dim$lon$len
	latsize <- nc_tmp$dim$lat$len
	# Loop over grid array
	for (x in 1:lonsize) {
		for (y in 1:latsize) {
			# Get primary land cover, longitude, and latitude 
			# for current grid cell			#
			data <- ncvar_get(nc_tmp, variable, 
				start=c(x,y,1), count=c(1,1,1))
			longitude <- ncvar_get(nc_tmp, "lon", start=x, count=1)
			latitude <- ncvar_get(nc_tmp, "lat", start=y, count=1)			
			# Check if current grid is land or water:
			# 00  open water                                                   
            # 01  inland water                                                 
			# if (!(data == 00) && !(data == 01)) {			
				# cat(x, "\t", y, "\t", longitude, "\t", latitude, "\n",
					# file=outfile, sep="", append=TRUE)			
			# }
			cat(x, "\t", y, "\t", longitude, "\t", latitude, "\n",
				file=outfile, sep="", append=TRUE)			
		}		
	}
	nc_close(nc_tmp)
}

# Now run it
get_agera5_grid()


# Faster version
get_agera5_grid_land <- function(workdir="/home/luigi/LUIGI/agera5", infile="Solar-Radiation-Flux_C3S-glob-agric_AgERA5_daily_20171201-20171231_final-v1.0.nc", variable="Solar_Radiation_Flux", outfile="agera5_grid_land.txt") {
	require(ncdf4)
	# Dir for reading data
	setwd(workdir)
	# open netCDF
	nc_tmp <- nc_open(infile)	
	# Print header line
	cat("x", "\t", "y", "\t", "lon", "\t", "lat", "\n",
		file=outfile, sep="")
	# Get geographic dimensions
	lonsize <- nc_tmp$dim$lon$len
	latsize <- nc_tmp$dim$lat$len
	# Read lat, lon, and first day of data into vectors
	longitude <- ncvar_get(nc_tmp, "lon", start=1, count=lonsize)
	latitude <- ncvar_get(nc_tmp, "lat", start=1, count=latsize)
	data_values <- ncvar_get(nc_tmp, variable, start=c(1,1,1), count=c(lonsize,latsize,1))

	# Debugging code follows
	# results <- list(longitude, latitude, data_values)
	# return(results)
	# stop()			

	# Loop over grid array
	for (x in 1:lonsize) {
		for (y in 1:latsize) {
			# Check NA, longitude, and latitude 
			# for current grid cell
			if(is.na(data_values[x,y])) next
			# longitude <- ncvar_get(nc_tmp, "lon", start=x, count=1)
			# latitude <- ncvar_get(nc_tmp, "lat", start=y, count=1)			
			cat(x, "\t", y, "\t", longitude[x], "\t", latitude[y], "\n",
				file=outfile, sep="", append=TRUE)			
		}
	}
	nc_close(nc_tmp)
}

# Now run it
get_agera5_grid_land()



# Little function to print info on nc r objects
ncinfoToFile <- function(ncobjname, txtoutfile) {
# ncobjname is where nc_open was assigned
# txtoutfile is of type tmp_dump.txt
sink(txtoutfile)
print(ncobjname)
sink()
}

# The following is old stuff from agmerra

# ls()
# [1] "nc_tmp_humi" "nc_tmp_prcp" "nc_tmp_srad" "nc_tmp_tmax"
# [5] "nc_tmp_tmin" "nc_tmp_wndm" "nc_tmp_wndz"

ncinfoToFile(nc_tmp_tmax, "nc_tmp_tmax.txt")
ncinfoToFile(nc_tmp_tmin, "nc_tmp_tmin.txt")
ncinfoToFile(nc_tmp_prcp, "nc_tmp_prcp.txt")
ncinfoToFile(nc_tmp_srad, "nc_tmp_srad.txt")
ncinfoToFile(nc_tmp_humi, "nc_tmp_humi.txt")
ncinfoToFile(nc_tmp_wndz, "nc_tmp_wndz.txt")
ncinfoToFile(nc_tmp_wndm, "nc_tmp_wndm.txt")

ndims <- nc_tmp_tmax$var[["tasmax"]]$ndims
ndays <- nc_tmp_tmax$var[["tasmax"]]$varsize[ndims]



