# extract_grid_nex-gddp.R
# Author: Luigi Ponti quartese gmail.com
# Copyright: (c) 2006 CASAS (Center for the Analysis of Sustainable Agricultural Systems, https://www.casasglobal.org/)
# SPDX-License-Identifier: GPL-3.0-or-later
# 2018-03-06
# Extract coordinates from netCDF grid
# Functionality from this script is now included in netcdf_grid_extract.py

# NEX Global Daily Downscaled Climate Projections.
# https://nex.nasa.gov/nex/projects/1356/

# The R side

# After istalling ncdf4 from local package

mv -iv *rcp85*.nc MPI-ESM-LR_rcp85/
mv -iv *historical*.nc MPI-ESM-LR_historical/

# in R Studio

library(ncdf4)

setwd("/home/luigi/LUIGI/nex_gddp")

ncin <- nc_open("MPI-ESM-LR_rcp85/tasmax_day_BCSD_rcp85_r1i1p1_MPI-ESM-LR_2045.nc")

# https://www.r-bloggers.com/a-netcdf-4-in-r-cheatsheet/
# Save the print(nc) dump to a text file (same name as the nc file with a txt extension)
sink(paste0("pr_day_BCSD_historical_r1i1p1_MPI-ESM-LR_1982.nc", ".txt"))
print(ncin)
sink()

# Get a list of the NetCDF's R attributes:
attributes(ncin)$names

[1] "filename"    "writable"    "id"         
 [4] "safemode"    "format"      "is_GMT"     
 [7] "groups"      "fqgn2Rindex" "ndims"      
[10] "natts"       "dim"         "unlimdimid" 
[13] "nvars"       "var"  

print(paste("The file has",ncin$nvars,"variables,",ncin$ndims,"dimensions and",ncin$natts,"NetCDF attributes"))

[1] "The file has 1 variables, 3 dimensions and 34 NetCDF attributes"

# Get a list of the nc variable names.
attributes(ncin$var)$names
[1] "pr"

# Take a look at the chlorophyll variable's nc attributes (units etc).
ncatt_get(ncin, attributes(ncin$var)$names[1])
# or
ncatt_get(ncin, "pr")
$time
[1] 47481.5

$standard_name
[1] "precipitation_flux"

$long_name
[1] "Precipitation"

$comment
[1] "at surface; includes both liquid and solid phases from all types of clouds (both large-scale and convective)"

$units
[1] "kg m-2 s-1"

$cell_methods
[1] "time: mean"

$cell_measures
[1] "area: areacella"

$history
[1] "2011-05-28T05:35:12Z altered by CMOR: replaced missing value flag (2e+20) with standard missing value (1e+20)."

$missing_value
[1] 1e+20

$associated_files
[1] "baseURL: http://cmip-pcmdi.llnl.gov/CMIP5/dataLocation gridspecFile: gridspec_atmos_fx_MPI-ESM-LR_historical_r0i0p0.nc areacella: areacella_fx_MPI-ESM-LR_historical_r0i0p0.nc"

$`_FillValue`
[1] 1e+20



# Retrieve a matrix of the chlorophyll data using the ncvar_get function:
prcp <- ncvar_get(ncin, "pr")

# Print the data's dimensions
dim(prcp)

[1] 1440  720  365

# Retrieve the latitude and longitude values.
> attributes(ncin$dim$lat)$names
 [1] "name"          "len"           "unlim"        
 [4] "group_index"   "group_id"      "id"           
 [7] "dimvarid"      "units"         "vals"         
[10] "create_dimvar"

latsize <- ncin$dim$lat$len
latsize
[1] 720

lonsize <- ncin$dim$lon$len
lonsize
[1] 1440

longitude <- ncvar_get(ncin, "lon", start=lonsize, count=1)


# Close after you are done
nc_close(ncin)

#https://stat.ethz.ch/R-manual/R-devel/library/base/html/as.Date.html
date <- as.Date(10071, origin = "1980-01-01")
## date given as number of days since 1900-01-01 (a date in 1989)
cat(format(date, format="%m\t%d\t%Y"))



# Function to get coordinates of grid cells with no water (i.e., land)
get_nexgddp_grid <- function(workdir='/Users/luigi/Documents/maxtor/pending projects/CASAS object oriented models/McKnight/2025-07-26 pbdm web platform markus neteler', infile="tasmax_day_MPI-ESM1-2-HR_ssp585_r1i1p1f1_gn_2100_v2.0.nc", variable="tasmax", outfile="MPI-ESM1-2-HR_grid_tasmax_old_R.txt") {
	require(ncdf4)
	# Dir for reading data
	setwd(workdir)
	# open netCDF
	nc_tmp <- nc_open(infile)	
	# Print header linear
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
get_nexgddp_grid ()



# Little function to print info on nc r objects
ncinfoToFile <- function(ncobjname, txtoutfile) {
# ncobjname is where nc_open was assigned
# txtoutfile is of tipe tmp_dump.txt
sink(txtoutfile)
print(ncobjname)
sink()
}

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



