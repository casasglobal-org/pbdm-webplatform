# GRASS commands used for developing olive GIS layers.
# This is more a list to record commands used than a script intended to be
# simply run unattended.
# Author: Luigi Ponti quartese gmail com


# Import Coastline (version 4.1.0) 
# Source: https://www.naturalearthdata.com/ (public domain data)
v.in.ogr dsn=.\data\ne_10m_coastline layer=ne_10m_coastline output=ne_10m_coastline

# Import Admin 0 – Countries (version 4.1.0) 
# Source: https://www.naturalearthdata.com/ (public domain data)
v.in.ogr dsn=.\data\ne_10m_admin_0_countries_lakes layer=ne_10m_admin_0_countries_lakes output=ne_10m_admin_0_countries_lakes

# Andalusia
v.extract ne_10m_admin_0_countries_lakes out=spain where="NAME = 'Spain'"
v.extract ne_10m_admin_1_states_provinces_lakes out=andalusia_provinces where="region_cod = 'ES.AN'"
v.extract ne_10m_populated_places out=andalusia_cities where="(NAMEASCII = 'Almeria') or (NAMEASCII = 'Malaga') or (NAMEASCII = 'Jaen') or (NAMEASCII = 'Huelva') or (NAMEASCII = 'Cadiz') or (NAMEASCII = 'Granada') or (NAMEASCII = 'Cordoba') or (NAMEASCII = 'Seville')"

# Province names:
# Almeria
# Malaga
# Jaen
# Huelva
# Cadiz
# Granada
# Cordoba
# Seville

# Export to ESRI shapefile for use as area of interest (AOI)
v.out.ogr -c -e --verbose input=andalusia_provinces@luigi type=area dsn=andalusia_provinces
# Exporting 8 areas (may take some time)...
# Warning 1: One or several characters couldn't be converted
# correctly from UTF-8 to ISO-8859-1.
# This warning will not be emitted anymore.
# v.out.ogr complete. 8 features written to <andalusia_provinces> (ESRI_Shapefile).

# Andalusia bounding box
g.region -b vect=andalusia_provinces
# north latitude:   38:43:42.281643N
# south latitude:   36:00:23.240866N
# west longitude:   7:31:46.886574W
# east longitude:   1:38:29.823767W
# center longitude: 4:35:08.35517W
# center latitude:  37:22:02.761254N

# Simplified Andalusia bounding box
# north latitude:   40N
# south latitude:   34N
# west longitude:   9W
# east longitude:   0W

# Colombia
v.extract ne_10m_admin_0_countries_lakes out=colombia where="NAME = 'Colombia'"
v.extract ne_10m_admin_1_states_provinces_lakes out=colombia_departments where="admin = 'Colombia'"
v.extract ne_10m_populated_places out=colombia_cities where="ADM0NAME = 'Colombia'"

# Colombia bounding box
g.region -b vect=colombia                                      
# north latitude:   13:34:42.078756N
# south latitude:   4:14:11.344117S
# west longitude:   81:43:25.332888W
# east longitude:   66:52:30.218117W
# center longitude: 74:17:57.775502W
# center latitude:  4:40:15.367319N

# Simplified Colombia bounding box
# north latitude:   15N
# south latitude:   6S
# west longitude:   83W
# east longitude:   65W

# Associated SQLite database was exported to
# ne_10m_admin_0_countries_lakes.csv
# using https://sqlitebrowser.org/ 

# Import Admin 1 – States, Provinces (version 4.1.0) 
# Source: https://www.naturalearthdata.com/ (public domain data)
v.in.ogr dsn=.\casas_pbdm_olive\data\ne_10m_admin_1_states_provinces_lakes layer=ne_10m_admin_1_states_provinces_lakes output=ne_10m_admin_1_states_provinces_lakes

# Associated SQLite database was exported to
# ne_10m_admin_1_states_provinces_lakes.csv
# using https://sqlitebrowser.org/ 

# Get a labeled raster for area statistics
# (needs to be run in projected location,
# but test run performed also in latlong)
# Andalusia
v.to.rast in=andalusia_provinces out=andalusia_provinces use=attr col=cat labelcol=iso_3166_2
# Colombia
v.to.rast in=colombia_departments out=colombia_departments use=attr col=cat labelcol=iso_3166_2

# Import Populated Places (version 4.1.0) 
# Source: https://www.naturalearthdata.com/ (public domain data)
v.in.ogr dsn=.\data\ne_10m_populated_places layer=ne_10m_populated_places output=ne_10m_populated_places

# Associated SQLite database was exported to
# ne_10m_populated_places.csv
# using https://sqlitebrowser.org/ 

# Import digital elevation model from based EarthEnv (dataset=elevation, 
# aggregation=median, sources=GMTED2010, resolution=1km)
# https://www.earthenv.org/topography
# see Amatulli et al. (2018) https://doi.org/10.1038/sdata.2018.40
r.in.gdal input=.\data\elevation_1KMmd_GMTEDmd.tif output=elevation_1KMmd_GMTEDmd

# Import 1:10m Shaded Relief (version 2.1.0)
# Source: https://www.naturalearthdata.com/ (public domain data)
r.in.gdal input=.\data\SR_HR\SR_HR.tif output=SR_HR

r.info map=SR_HR
 # +----------------------------------------------------------------------------+
 # | Layer:    SR_HR@luigi                    Date: Mon Sep 09 15:53:59 2019    |
 # | Mapset:   luigi                          Login of Creator: Luigi           |
 # | Location: latlong                                                          |
 # | DataBase: C:\cygwin\home\andy                                              |
 # | Title:     ( SR_HR )                                                       |
 # | Timestamp: none                                                            |
 # |----------------------------------------------------------------------------|
 # |                                                                            |
 # |   Type of Map:  raster               Number of Categories: 0               |
 # |   Data Type:    CELL                                                       |
 # |   Rows:         10800                                                      |
 # |   Columns:      21600                                                      |
 # |   Total Cells:  233280000                                                  |
 # |        Projection: Latitude-Longitude                                      |
 # |            N:        90N    S:        90S   Res:  0:01                     |
 # |            E:       180E    W:       180W   Res:  0:01                     |
 # |   Range of data:    min = 36  max = 255                                    |
 # |                                                                            |
 # |   Data Description:                                                        |
 # |    generated by r.in.gdal                                                  |
 # |                                                                            |
 # |   Comments:                                                                |
 # |    r.in.gdal input="D:\maxtor\pending projects\h2020\SC5-01-2016-2017 E\   |
 # |    xploiting the added value\MED-GOLD\pbdm work med-gold\casas_pbdm_oli\   |
 # |    ve\data\SR_HR\SR_HR.tif" output="SR_HR"                                 |
 # |                                                                            |
 # +----------------------------------------------------------------------------+

# Import Gray Earth with Shaded Relief, Hypsography, Ocean Bottom, 
# and Drainages (version 2.1.0)
# Source: https://www.naturalearthdata.com/ (public domain data)
r.in.gdal input=.\data\GRAY_HR_SR_OB_DR\GRAY_HR_SR_OB_DR.tif output=GRAY_HR_SR_OB_DR

r.info map=GRAY_HR_SR_OB_DR                                            
 # +----------------------------------------------------------------------------+
 # | Layer:    GRAY_HR_SR_OB_DR@luigi         Date: Mon Sep 09 16:19:01 2019    |
 # | Mapset:   luigi                          Login of Creator: Luigi           |
 # | Location: latlong                                                          |
 # | DataBase: C:\cygwin\home\andy                                              |
 # | Title:     ( GRAY_HR_SR_OB_DR )                                            |
 # | Timestamp: none                                                            |
 # |----------------------------------------------------------------------------|
 # |                                                                            |
 # |   Type of Map:  raster               Number of Categories: 0               |
 # |   Data Type:    CELL                                                       |
 # |   Rows:         10800                                                      |
 # |   Columns:      21600                                                      |
 # |   Total Cells:  233280000                                                  |
 # |        Projection: Latitude-Longitude                                      |
 # |            N:        90N    S:        90S   Res:  0:01                     |
 # |            E:       180E    W:       180W   Res:  0:01                     |
 # |   Range of data:    min = 42  max = 254                                    |
 # |                                                                            |
 # |   Data Description:                                                        |
 # |    generated by r.in.gdal                                                  |
 # |                                                                            |
 # |   Comments:                                                                |
 # |    r.in.gdal input="D:\maxtor\pending projects\h2020\SC5-01-2016-2017 E\   |
 # |    xploiting the added value\MED-GOLD\pbdm work med-gold\casas_pbdm_oli\   |
 # |    ve\data\GRAY_HR_SR_OB_DR\GRAY_HR_SR_OB_DR.tif" output="GRAY_HR_SR_OB\   |
 # |    _DR"                                                                    |
 # |                                                                            |
 # +----------------------------------------------------------------------------+

# Import Natural Earth I with Shaded Relief, Water, 
# and Drainages (version 2.0.0) 
# Source: https://www.naturalearthdata.com/ (public domain data)
r.in.gdal input=.\data\NE1_HR_LC_SR_W_DR\NE1_HR_LC_SR_W_DR.tif output=NE1_HR_LC_SR_W_DR

r.info map=NE1_HR_LC_SR_W_DR.blue
 # +----------------------------------------------------------------------------+
 # | Layer:    NE1_HR_LC_SR_W_DR.blue@luigi   Date: Mon Sep 09 16:35:31 2019    |
 # | Mapset:   luigi                          Login of Creator: Luigi           |
 # | Location: latlong                                                          |
 # | DataBase: C:\cygwin\home\andy                                              |
 # | Title:     ( NE1_HR_LC_SR_W_DR.blue )                                      |
 # | Timestamp: none                                                            |
 # |----------------------------------------------------------------------------|
 # |                                                                            |
 # |   Type of Map:  raster               Number of Categories: 0               |
 # |   Data Type:    CELL                                                       |
 # |   Rows:         10800                                                      |
 # |   Columns:      21600                                                      |
 # |   Total Cells:  233280000                                                  |
 # |        Projection: Latitude-Longitude                                      |
 # |            N:        90N    S:        90S   Res:  0:01                     |
 # |            E:       180E    W:       180W   Res:  0:01                     |
 # |   Range of data:    min = 91  max = 255                                    |
 # |                                                                            |
 # |   Data Description:                                                        |
 # |    generated by r.in.gdal                                                  |
 # |                                                                            |
 # |   Comments:                                                                |
 # |    r.in.gdal input="D:\maxtor\pending projects\h2020\SC5-01-2016-2017 E\   |
 # |    xploiting the added value\MED-GOLD\pbdm work med-gold\casas_pbdm_oli\   |
 # |    ve\data\NE1_HR_LC_SR_W_DR\NE1_HR_LC_SR_W_DR.tif" output="NE1_HR_LC_S\   |
 # |    R_W_DR"                                                                 |
 # |                                                                            |
 # +----------------------------------------------------------------------------+

# Natural Earth I data results in RGB layer:
# r.in.gdal complete. Raster map <NE1_HR_LC_SR_W_DR.red> created.
# r.in.gdal complete. Raster map <NE1_HR_LC_SR_W_DR.green> created.
# r.in.gdal complete. Raster map <NE1_HR_LC_SR_W_DR.blue> created.

# Import crop data for olive and coffee:

# Harvested Area: fractional:  Crop-specific data representing the average fractional proportion of a gridcell that was harvested in a crop during the 1997-2003 era.

# Yield: tons per hectare: Crop-specific data representing the average yield for a crop in tons per hectare during the 1997-2003 era

# Production: tons: Total crop production in metric tons on the land-area mass of a gridcell. Harvested area in hectares was multiplied by yield per hectare to create this data product.

# Source: http://www.earthstat.org/harvested-area-yield-175-crops/

# Olive
r.in.gdal input=.\data\olive_HarvAreaYield_Geotiff\olive_HarvestedAreaFraction.tif output=olive_HarvestedAreaFraction

r.info map=olive_HarvestedAreaFraction                                    
 # +----------------------------------------------------------------------------+
 # | Layer:    olive_HarvestedAreaFraction@l  Date: Mon Sep 09 17:36:23 2019    |
 # | Mapset:   luigi                          Login of Creator: Luigi           |
 # | Location: latlong                                                          |
 # | DataBase: C:\cygwin\home\andy                                              |
 # | Title:     ( olive_HarvestedAreaFraction )                                 |
 # | Timestamp: none                                                            |
 # |----------------------------------------------------------------------------|
 # |                                                                            |
 # |   Type of Map:  raster               Number of Categories: 0               |
 # |   Data Type:    FCELL                                                      |
 # |   Rows:         2160                                                       |
 # |   Columns:      4320                                                       |
 # |   Total Cells:  9331200                                                    |
 # |        Projection: Latitude-Longitude                                      |
 # |            N:        90N    S:        90S   Res:  0:05                     |
 # |            E:       180E    W:       180W   Res:  0:05                     |
 # |   Range of data:    min = 0  max = 0.8403285                               |
 # |                                                                            |
 # |   Data Description:                                                        |
 # |    generated by r.in.gdal                                                  |
 # |                                                                            |
 # |   Comments:                                                                |
 # |    r.in.gdal input="D:\maxtor\pending projects\h2020\SC5-01-2016-2017 E\   |
 # |    xploiting the added value\MED-GOLD\pbdm work med-gold\casas_pbdm_oli\   |
 # |    ve\data\olive_HarvAreaYield_Geotiff\olive_HarvestedAreaFraction.tif"\   |
 # |     output="olive_HarvestedAreaFraction"                                   |
 # |                                                                            |
 # +----------------------------------------------------------------------------+
    
r.in.gdal input=.\data\olive_HarvAreaYield_Geotiff\olive_YieldPerHectare.tif output=olive_YieldPerHectare

r.info map=olive_YieldPerHectare                                       
 # +----------------------------------------------------------------------------+
 # | Layer:    olive_YieldPerHectare@luigi    Date: Mon Sep 09 17:36:26 2019    |
 # | Mapset:   luigi                          Login of Creator: Luigi           |
 # | Location: latlong                                                          |
 # | DataBase: C:\cygwin\home\andy                                              |
 # | Title:     ( olive_YieldPerHectare )                                       |
 # | Timestamp: none                                                            |
 # |----------------------------------------------------------------------------|
 # |                                                                            |
 # |   Type of Map:  raster               Number of Categories: 0               |
 # |   Data Type:    FCELL                                                      |
 # |   Rows:         2160                                                       |
 # |   Columns:      4320                                                       |
 # |   Total Cells:  9331200                                                    |
 # |        Projection: Latitude-Longitude                                      |
 # |            N:        90N    S:        90S   Res:  0:05                     |
 # |            E:       180E    W:       180W   Res:  0:05                     |
 # |   Range of data:    min = 0  max = 13.10736                                |
 # |                                                                            |
 # |   Data Description:                                                        |
 # |    generated by r.in.gdal                                                  |
 # |                                                                            |
 # |   Comments:                                                                |
 # |    r.in.gdal input="D:\maxtor\pending projects\h2020\SC5-01-2016-2017 E\   |
 # |    xploiting the added value\MED-GOLD\pbdm work med-gold\casas_pbdm_oli\   |
 # |    ve\data\olive_HarvAreaYield_Geotiff\olive_YieldPerHectare.tif" outpu\   |
 # |    t="olive_YieldPerHectare"                                               |
 # |                                                                            |
 # +----------------------------------------------------------------------------+
 
r.in.gdal input=.\data\olive_HarvAreaYield_Geotiff\olive_Production.tif output=olive_Production

r.info map=olive_Production                                        
 # +----------------------------------------------------------------------------+
 # | Layer:    olive_Production@luigi         Date: Mon Sep 09 17:44:40 2019    |
 # | Mapset:   luigi                          Login of Creator: Luigi           |
 # | Location: latlong                                                          |
 # | DataBase: C:\cygwin\home\andy                                              |
 # | Title:     ( olive_Production )                                            |
 # | Timestamp: none                                                            |
 # |----------------------------------------------------------------------------|
 # |                                                                            |
 # |   Type of Map:  raster               Number of Categories: 0               |
 # |   Data Type:    FCELL                                                      |
 # |   Rows:         2160                                                       |
 # |   Columns:      4320                                                       |
 # |   Total Cells:  9331200                                                    |
 # |        Projection: Latitude-Longitude                                      |
 # |            N:        90N    S:        90S   Res:  0:05                     |
 # |            E:       180E    W:       180W   Res:  0:05                     |
 # |   Range of data:    min = 0  max = 20050.11                                |
 # |                                                                            |
 # |   Data Description:                                                        |
 # |    generated by r.in.gdal                                                  |
 # |                                                                            |
 # |   Comments:                                                                |
 # |    r.in.gdal input="D:\maxtor\pending projects\h2020\SC5-01-2016-2017 E\   |
 # |    xploiting the added value\MED-GOLD\pbdm work med-gold\casas_pbdm_oli\   |
 # |    ve\data\olive_HarvAreaYield_Geotiff\olive_Production.tif" output="ol\   |
 # |    ive_Production"                                                         |
 # |                                                                            |
 # +----------------------------------------------------------------------------+

# Develop new raster mask for pure olive standings in Andalusia (Spain).
# TIF file Pure_olivar_wgs841.tif generated by Freddy Rivas González 
# frivas@gmv.com Spanish SIGPAC 2018 vector dataset applying filter 
# trough sql query. Data source:
# http://www.juntadeandalucia.es/agriculturaypesca/sigpac/index.xhtml
# (in latlong location)
# To do: implement in GIS script
r.import input="/Users/luigi/Documents/mac_maxtor/pending projects/h2020/SC5-01-2016-2017 Exploiting the added value/MED-GOLD/pbdm work med-gold/casas_gis_source_data_backup/andalusia_pure_olivar_sigpac/Pure_olivar_wgs841.tif" output=Pure_olivar_wgs841

# Information about the imported raster
r.info Pure_olivar_wgs841                                                       
 +----------------------------------------------------------------------------+
 | Map:      Pure_olivar_wgs841             Date: Mon Aug 31 20:03:09 2020    |
 | Mapset:   luigi                          Login of Creator: luigi           |
 | Location: latlong                                                          |
 | DataBase: /Users/luigi/grassdata                                           |
 | Title:                                                                     |
 | Timestamp: none                                                            |
 |----------------------------------------------------------------------------|
 |                                                                            |
 |   Type of Map:  raster               Number of Categories: 0               |
 |   Data Type:    CELL                                                       |
 |   Rows:         8307                                                       |
 |   Columns:      19124                                                      |
 |   Total Cells:  158863068                                                  |
 |        Projection: Latitude-Longitude                                      |
 |            N: 38:44:16.418788N    S: 36:09:37.465882N   Res: 0:00:01.11700 |
 |            E: 1:37:36.4W    W: 7:33:37.988078W   Res: 0:00:01.117004       |
 |   Range of data:    min = 1  max = 1                                       |
 |                                                                            |
 |   Data Description:                                                        |
 |    generated by r.proj                                                     |
 |                                                                            |
 |   Comments:                                                                |
 |    r.proj --quiet location="temp_import_location_14257" mapset="PERMANE\   |
 |    NT" input="Pure_olivar_wgs841" method="nearest" memory=300 resolutio\   |
 |    n=0.00031027892623914196                                                |
 |                                                                            |
 +----------------------------------------------------------------------------+
                         
r.stats -a -n input=Pure_olivar_wgs841@luigi
1 15513782081.114227 # m^2
# 15513,782081 km^2
# 1551378,2081 ha


# Move to projected location and reproject after getting
# region extent/resolution from source raster
r.proj -g input=Pure_olivar_wgs841 location=latlong mapset=luigi
# Adjust region before reprojecting
g.region n=147717.59799636 s=-139189.14898944 w=-251863.69121183 e=272456.50933925 rows=8307 cols=19124
# Reproject for good (originl resolution of about 30 m)
r.proj input=Pure_olivar_wgs841 location=latlong mapset=luigi
# Give it a decent name
g.rename rast=Pure_olivar_wgs841@medgold,olive_monoculture_sigpac_2018
# Change region resolution (Andalusia GIS script) and resample to
# 1 km
g.region -a res=1000    
r.resample input=olive_monoculture_sigpac_2018 output=olive_monoculture_sigpac_2018_1km
# 3 km
g.region -a res=3000    
r.resample input=olive_monoculture_sigpac_2018 output=olive_monoculture_sigpac_2018_3km
# 10 km
g.region -a res=10000  
r.resample input=olive_monoculture_sigpac_2018 output=olive_monoculture_sigpac_2018_10km

# Compare area after resampling
r.stats -a -n input=olive_monoculture_sigpac_2018
1 15982000000.000000
r.stats -a -n input=olive_monoculture_sigpac_2018_1km
1 15982000000.000000
r.stats -a -n input=olive_monoculture_sigpac_2018_3km
1 15867000000.000000
r.stats -a -n input=olive_monoculture_sigpac_2018_10km
1 16200000000.000000

r.grow input=olive_monoculture_sigpac_2018_1km output=olive_monoculture_sigpac_2018_1km_grow radius=10.01 old=1 new=1
r.stats -a -n input=olive_monoculture_sigpac_2018_1km_grow
1 80996000000.000000

r.grow input=olive_monoculture_sigpac_2018 output=olive_monoculture_sigpac_2018_grow_5000 radius=5.01 old=1 new=1
r.stats -a -n input=olive_monoculture_sigpac_2018_grow_5000
1 62352000000.000000

r.grow input=olive_monoculture_sigpac_2018 output=olive_monoculture_sigpac_2018_grow_3000 radius=3.01 old=1 new=1
r.stats -a -n input=olive_monoculture_sigpac_2018_grow_3000
1 49448000000.000000


# Coffee
r.in.gdal input=.\data\coffee_HarvAreaYield_Geotiff\coffee_HarvestedAreaFraction.tif output=coffee_HarvestedAreaFraction

r.info map=coffee_HarvestedAreaFraction                              
 # +----------------------------------------------------------------------------+
 # | Layer:    coffee_HarvestedAreaFraction@  Date: Mon Sep 09 18:24:09 2019    |
 # | Mapset:   luigi                          Login of Creator: Luigi           |
 # | Location: latlong                                                          |
 # | DataBase: C:\cygwin\home\andy                                              |
 # | Title:     ( coffee_HarvestedAreaFraction )                                |
 # | Timestamp: none                                                            |
 # |----------------------------------------------------------------------------|
 # |                                                                            |
 # |   Type of Map:  raster               Number of Categories: 0               |
 # |   Data Type:    FCELL                                                      |
 # |   Rows:         2160                                                       |
 # |   Columns:      4320                                                       |
 # |   Total Cells:  9331200                                                    |
 # |        Projection: Latitude-Longitude                                      |
 # |            N:        90N    S:        90S   Res:  0:05                     |
 # |            E:       180E    W:       180W   Res:  0:05                     |
 # |   Range of data:    min = 0  max = 0.9535263                               |
 # |                                                                            |
 # |   Data Description:                                                        |
 # |    generated by r.in.gdal                                                  |
 # |                                                                            |
 # |   Comments:                                                                |
 # |    r.in.gdal input="D:\maxtor\pending projects\h2020\SC5-01-2016-2017 E\   |
 # |    xploiting the added value\MED-GOLD\pbdm work med-gold\casas_pbdm_oli\   |
 # |    ve\data\coffee_HarvAreaYield_Geotiff\coffee_HarvestedAreaFraction.ti\   |
 # |    f" output="coffee_HarvestedAreaFraction"                                |
 # |                                                                            |
 # +----------------------------------------------------------------------------+

r.in.gdal input=.\data\coffee_HarvAreaYield_Geotiff\coffee_Production.tif output=coffee_Production

r.info map=coffee_Production                                        
 # +----------------------------------------------------------------------------+
 # | Layer:    coffee_Production@luigi        Date: Mon Sep 09 18:24:11 2019    |
 # | Mapset:   luigi                          Login of Creator: Luigi           |
 # | Location: latlong                                                          |
 # | DataBase: C:\cygwin\home\andy                                              |
 # | Title:     ( coffee_Production )                                           |
 # | Timestamp: none                                                            |
 # |----------------------------------------------------------------------------|
 # |                                                                            |
 # |   Type of Map:  raster               Number of Categories: 0               |
 # |   Data Type:    FCELL                                                      |
 # |   Rows:         2160                                                       |
 # |   Columns:      4320                                                       |
 # |   Total Cells:  9331200                                                    |
 # |        Projection: Latitude-Longitude                                      |
 # |            N:        90N    S:        90S   Res:  0:05                     |
 # |            E:       180E    W:       180W   Res:  0:05                     |
 # |   Range of data:    min = 0  max = 7355.236                                |
 # |                                                                            |
 # |   Data Description:                                                        |
 # |    generated by r.in.gdal                                                  |
 # |                                                                            |
 # |   Comments:                                                                |
 # |    r.in.gdal input="D:\maxtor\pending projects\h2020\SC5-01-2016-2017 E\   |
 # |    xploiting the added value\MED-GOLD\pbdm work med-gold\casas_pbdm_oli\   |
 # |    ve\data\coffee_HarvAreaYield_Geotiff\coffee_Production.tif" output="\   |
 # |    coffee_Production"                                                      |
 # |                                                                            |
 # +----------------------------------------------------------------------------+

r.in.gdal input=.\data\coffee_HarvAreaYield_Geotiff\coffee_YieldPerHectare.tif output=coffee_YieldPerHectare

r.info map=coffee_YieldPerHectare                                 
 # +----------------------------------------------------------------------------+
 # | Layer:    coffee_YieldPerHectare@luigi   Date: Mon Sep 09 18:24:14 2019    |
 # | Mapset:   luigi                          Login of Creator: Luigi           |
 # | Location: latlong                                                          |
 # | DataBase: C:\cygwin\home\andy                                              |
 # | Title:     ( coffee_YieldPerHectare )                                      |
 # | Timestamp: none                                                            |
 # |----------------------------------------------------------------------------|
 # |                                                                            |
 # |   Type of Map:  raster               Number of Categories: 0               |
 # |   Data Type:    FCELL                                                      |
 # |   Rows:         2160                                                       |
 # |   Columns:      4320                                                       |
 # |   Total Cells:  9331200                                                    |
 # |        Projection: Latitude-Longitude                                      |
 # |            N:        90N    S:        90S   Res:  0:05                     |
 # |            E:       180E    W:       180W   Res:  0:05                     |
 # |   Range of data:    min = 0  max = 9.787734                                |
 # |                                                                            |
 # |   Data Description:                                                        |
 # |    generated by r.in.gdal                                                  |
 # |                                                                            |
 # |   Comments:                                                                |
 # |    r.in.gdal input="D:\maxtor\pending projects\h2020\SC5-01-2016-2017 E\   |
 # |    xploiting the added value\MED-GOLD\pbdm work med-gold\casas_pbdm_oli\   |
 # |    ve\data\coffee_HarvAreaYield_Geotiff\coffee_YieldPerHectare.tif" out\   |
 # |    put="coffee_YieldPerHectare"                                            |
 # |                                                                            |
 # +----------------------------------------------------------------------------+

# Get centroid coordinates for mainland Andalusia
# First, dissolve Andalusia boundaries to get single area
# which is needed for obtaining a centroid for Andalusia 
v.dissolve andalusia_provinces output=andalusia column=postal
# Remove centroid as one of the province centroid was used
v.edit map=andalusia type=centroid tool=delete cats=1
# Add centroid again where it supposed to be (center of gravity)
v.centroids in=andalusia out=andalusia_cntrd option=add
# Rename to original Andalusia vector
g.rename --overwrite vect=andalusia_cntrd,andalusia
# Extract centroid to get coordinates
v.extract in=andalusia out=andalusia_centroid type=centroid
v.out.ascii andalusia_centroid
# -4.7608617|37.44750952|1
# Alternatively, one can add columns to store coordinates
v.db.addcol map=andalusia_centroid col="x double,y double,z double"
# Then insert coords in x,y,z columns
v.to.db map=andalusia_centroid option=coor col=x,y,z

# Get centroid coordinates for mainland Colombia
# for use to set up a Lambert Azimuthal Equal Area
# Extract centroids from polygon map
v.extract in=colombia out=colombia_centroids type=centroid
# Create points where centroids are (each new point gets a new category)
v.to.points in=colombia_centroids out=colombia_centroids_points
# Print coordinates for new points (with categories)
v.out.ascii colombia_centroids_points layer=2
# -78.15944454|2.59946779|1
# -77.86189282|2.62916728|2
# -77.82385718|2.66334724|3
# -77.41781699|4.25979037|4
# -81.70522747|12.54534552|5
# -81.36746449|13.3458128|6
# -81.59743004|3.9760397|7
# -78.18867384|2.96271771|8
# -75.57014123|10.34916796|9
# -80.09013649|13.57747243|10
# -73.06780142|4.35730071|11 *** centroid for mainland Colombia ***

# Alternatively, one can add columns to store coordinates
v.db.addcol map=colombia_centroids_points layer=2 col="x double,y double,z double"

# Then insert coords in x,y,z columns
v.to.db map=colombia_centroids_points layer=2 option=coor col=x,y,z

# Define equal-area projected locations 
# for mapping Andalusia and Colombia

# laea_andalusia
# Lambert Azimuthal Equal Area centered on Andalusia centroid
# Central parallel 37.448
# Central meridian -4.761
g.proj -p                                                                   
# -PROJ_INFO-------------------------------------------------
# name       : Lambert Azimuthal Equal Area
# proj       : laea
# lat_0      : 37.448
# lon_0      : -4.761
# x_0        : 0
# y_0        : 0
# no_defs    : defined
# datum      : wgs84
# ellps      : wgs84
# towgs84    : 0.000,0.000,0.000
# -PROJ_UNITS------------------------------------------------
# unit       : meter
# units      : meters
# meters     : 1

# laea_colombia
# Lambert Azimuthal Equal Area centered on Colombia centroid
# Central parallel 4.357
# Central meridian -73.068
g.proj -p 
# -PROJ_INFO-------------------------------------------------
# name       : Lambert Azimuthal Equal Area
# proj       : laea
# lat_0      : 4.357
# lon_0      : -73.068
# x_0        : 0
# y_0        : 0
# no_defs    : defined
# datum      : wgs84
# ellps      : wgs84
# towgs84    : 0.000,0.000,0.000
# -PROJ_UNITS------------------------------------------------
# unit       : meter
# units      : meters
# meters     : 1

# Reproject all data and set region extents
# That is, reproject andalusia and colobmia,
# then set region extents,
# then import rasters and vectors,
# and finally develop some extra layers,
# such as a labeled raster for area statistics (see below)

# Andalusia
v.proj in=andalusia location=latlong mapset=luigi
g.region vect=andalusia
# Make some room on the margins
g.region n=n+100000 s=s-100000 e=e+100000 w=w-100000
# Import more vectors based on current region extent
v.proj in=andalusia_provinces location=latlong mapset=luigi
v.proj in=andalusia_cities location=latlong mapset=luigi
# Get a region box for clipping world vectors in latlong location
v.in.region output=andalusia_region_box
# Go back to latlong and clip country boundaries and coastline
v.proj in=andalusia_region_box location=laea_andalusia mapset=medgold
v.select ainput=ne_10m_admin_0_countries_lakes binput=andalusia_region_box output=ne_10m_admin_0_countries_lakes_andalusia operator=overlap
v.select ainput=ne_10m_coastline binput=andalusia_region_box output=ne_10m_coastline_andalusia operator=overlap
# Reproject in laea after clipping
v.proj in=ne_10m_admin_0_countries_lakes_andalusia location=latlong mapset=luigi
v.proj in=ne_10m_coastline_andalusia location=latlong mapset=luigi

# Check extent (actually, the extent is the region) but more
# importantly the resolution of rasters before reprojecting
# rasters
# Crop data

# For rasters, first do region clipping in latlong location
# Rasters with 5 min resolution
g.region rast=olive_Production
g.region -a vect=andalusia_region_box
r.mapcalc "olive_HarvestedAreaFraction_andalusia=olive_HarvestedAreaFraction"
r.mapcalc "olive_Production_andalusia=olive_Production"
r.mapcalc "olive_YieldPerHectare_andalusia=olive_YieldPerHectare"
# Rasters with 1 min resolution
g.region rast=SR_HR
g.region -a vect=andalusia_region_box
r.mapcalc "SR_HR_andalusia = SR_HR"
r.mapcalc "GRAY_HR_SR_OB_DR_andalusia = GRAY_HR_SR_OB_DR"
r.mapcalc "NE1_HR_LC_SR_W_DR.blue_andalusia = NE1_HR_LC_SR_W_DR.blue"
r.mapcalc "NE1_HR_LC_SR_W_DR.green_andalusia = NE1_HR_LC_SR_W_DR.green"
r.mapcalc "NE1_HR_LC_SR_W_DR.red_andalusia = NE1_HR_LC_SR_W_DR.red"
# Rasters with 30 sec resolution
g.region rast=elevation_1KMmd_GMTEDmd
g.region -a vect=andalusia_region_box
r.mapcalc "elevation_1KMmd_GMTEDmd_andalusia = elevation_1KMmd_GMTEDmd"

# Move to projected location and reproject after getting
# region extent/resolution from source clipped raster
# Rasters with 5 min resolution
r.proj -g input=olive_Production_andalusia location=latlong mapset=luigi
# n=246026.06737938 s=-263735.04233398 w=-371663.72261463 e=380260.64655069 rows=55 cols=102
g.region n=246026.06737938 s=-263735.04233398 w=-371663.72261463 e=380260.64655069 rows=55 cols=102
r.proj input=olive_Production_andalusia location=latlong mapset=luigi
r.proj input=olive_HarvestedAreaFraction_andalusia location=latlong mapset=luigi
r.proj input=olive_YieldPerHectare_andalusia location=latlong mapset=luigi
# Rasters with 1 min resolution
r.proj -g input=SR_HR_andalusia location=latlong mapset=luigi
# n=244042.14884332 s=-260231.8734701 w=-366953.26846418 e=377490.21562786 rows=272 cols=505
g.region n=244042.14884332 s=-260231.8734701 w=-366953.26846418 e=377490.21562786 rows=272 cols=505
r.proj input=SR_HR_andalusia location=latlong mapset=luigi
r.proj input=GRAY_HR_SR_OB_DR_andalusia location=latlong mapset=luigi
r.proj input=NE1_HR_LC_SR_W_DR.blue_andalusia location=latlong mapset=luigi
r.proj input=NE1_HR_LC_SR_W_DR.green_andalusia location=latlong mapset=luigi
r.proj input=NE1_HR_LC_SR_W_DR.red_andalusia location=latlong mapset=luigi
# Rasters with 30 sec resolution
r.proj -g input=elevation_1KMmd_GMTEDmd_andalusia location=latlong mapset=luigi  
# n=244008.52021571 s=-260263.72165408 w=-366193.66345343 e=376775.10543189 rows=544 cols=1008
g.region n=244008.52021571 s=-260263.72165408 w=-366193.66345343 e=376775.10543189 rows=544 cols=1008
r.proj input=elevation_1KMmd_GMTEDmd_andalusia location=latlong mapset=luigi
# Get a labeled raster for area statistics
# (check spatial resolution)
# Andalusia
g.region -a res=1000
v.to.rast in=andalusia_provinces out=andalusia_provinces use=attr col=cat labelcol=iso_3166_2

# Resample rasters to 250m resolution for improved display 
g.region -a res=250
r.resamp.interp input=SR_HR_andalusia output=SR_HR_andalusia_250m method=bicubic
r.resamp.interp input=GRAY_HR_SR_OB_DR_andalusia output=GRAY_HR_SR_OB_DR_andalusia_250m method=bicubic
r.resamp.interp input=NE1_HR_LC_SR_W_DR.blue_andalusia output=NE1_HR_LC_SR_W_DR.blue_andalusia_250m method=bicubic
r.resamp.interp input=NE1_HR_LC_SR_W_DR.green_andalusia output=NE1_HR_LC_SR_W_DR.green_andalusia_250m method=bicubic
r.resamp.interp input=NE1_HR_LC_SR_W_DR.red_andalusia output=NE1_HR_LC_SR_W_DR.red_andalusia_250m method=bicubic
# Make composite RGB raster
r.composite red=NE1_HR_LC_SR_W_DR.red_andalusia_250m green=NE1_HR_LC_SR_W_DR.green_andalusia_250m blue=NE1_HR_LC_SR_W_DR.blue_andalusia_250m output=NE1_HR_LC_SR_W_DR.composite_andalusia_250m
# Clip shaded relief
v.to.rast input=ne_10m_admin_0_countries_lakes_andalusia output=ne_10m_admin_0_countries_lakes_andalusia use=val value=1
r.mapcalc "SR_HR_andalusia_clip = if (ne_10m_admin_0_countries_lakes_andalusia, SR_HR_andalusia, null())"
r.colors map=SR_HR_andalusia_clip raster=SR_HR_andalusia
r.mapcalc "SR_HR_andalusia_clip_inverse = if (isnull(andalusia_provinces), SR_HR_andalusia_clip, null())"
r.colors map=SR_HR_andalusia_clip_inverse raster=SR_HR_andalusia
# Clip resampled shaded relief
r.mapcalc "SR_HR_andalusia_clip_250m = if (ne_10m_admin_0_countries_lakes_andalusia, SR_HR_andalusia_250m, null())"
r.colors map=SR_HR_andalusia_clip_250m raster=SR_HR_andalusia_250m
r.mapcalc "SR_HR_andalusia_clip_inverse_250m = if (isnull(andalusia_provinces), SR_HR_andalusia_clip_250m, null())"
r.colors map=SR_HR_andalusia_clip_inverse_250m raster=SR_HR_andalusia_250m
#################################################
# Region for the Andalusia mapping routine
g.region vect=andalusia_provinces
# Make some room on the margins
g.region n=n+10000 s=s-10000 e=e+10000 w=w-10000
# Align with resolution
g.region -a res=1000
#################################################
# Test statistics report
r.report -en map=andalusia_provinces,olive_HarvestedAreaFraction_andalusia units=k,c,p nsteps=4
# +-----------------------------------------------------------------------------+
# |                         RASTER MAP CATEGORY REPORT                          |
# |LOCATION: laea_andalusia                             Tue Sep 24 23:02:29 2019|
# |-----------------------------------------------------------------------------|
# |          north:  153000    east:  287000                                    |
# |REGION    south: -170000    west: -255000                                    |
# |          res:      1000    res:     1000                                    |
# |-----------------------------------------------------------------------------|
# |MASK: none                                                                   |
# |-----------------------------------------------------------------------------|
# |MAPS: Rasterized vector map from labels (andalusia_provinces in medgold)     |
# |        (untitled) (olive_HarvestedAreaFraction_andalusia in medgold)        |
# |-----------------------------------------------------------------------------|
# |                Category Information                 |  square  | cell|   %  |
# |   #|description                                     |kilometers|count| cover|
# |-----------------------------------------------------------------------------|
# |1290|ES-CA                                           |  7306.000| 7306|  8.39|
# |    |------------------------------------------------|----------|-----|------|
# |    |       0-0.088773|from  to . . . . . . . . . . .|  3900.000| 3900| 53.38|
# |    |0.088773-0.177547|from  to . . . . . . . . . . .|   797.000|  797| 10.91|
# |    | 0.177547-0.26632|from  to . . . . . . . . . . .|  1139.000| 1139| 15.59|
# |    | 0.26632-0.355094|from  to . . . . . . . . . . .|  1470.000| 1470| 20.12|
# |-----------------------------------------------------|----------|-----|------|
# |1688|ES-H                                            |  9986.000| 9986| 11.47|
# |    |------------------------------------------------|----------|-----|------|
# |    |       0-0.088773|from  to . . . . . . . . . . .|  6934.000| 6934| 69.44|
# |    |0.088773-0.177547|from  to . . . . . . . . . . .|  1065.000| 1065| 10.66|
# |    | 0.177547-0.26632|from  to . . . . . . . . . . .|   788.000|  788|  7.89|
# |    | 0.26632-0.355094|from  to . . . . . . . . . . .|  1199.000| 1199| 12.01|
# |-----------------------------------------------------|----------|-----|------|
# |2503|ES-AL                                           |  8676.000| 8676|  9.96|
# |    |------------------------------------------------|----------|-----|------|
# |    |       0-0.088773|from  to . . . . . . . . . . .|  3485.000| 3485| 40.17|
# |    |0.088773-0.177547|from  to . . . . . . . . . . .|  3038.000| 3038| 35.02|
# |    | 0.177547-0.26632|from  to . . . . . . . . . . .|  1774.000| 1774| 20.45|
# |    | 0.26632-0.355094|from  to . . . . . . . . . . .|   379.000|  379|  4.37|
# |-----------------------------------------------------|----------|-----|------|
# |2504|ES-GR                                           |12,636.000|12636| 14.51|
# |    |------------------------------------------------|----------|-----|------|
# |    |       0-0.088773|from  to . . . . . . . . . . .|  1229.000| 1229|  9.73|
# |    |0.088773-0.177547|from  to . . . . . . . . . . .|  2976.000| 2976| 23.55|
# |    | 0.177547-0.26632|from  to . . . . . . . . . . .|  3204.000| 3204| 25.36|
# |    | 0.26632-0.355094|from  to . . . . . . . . . . .|  5227.000| 5227| 41.37|
# |-----------------------------------------------------|----------|-----|------|
# |2505|ES-MA                                           |  7131.000| 7131|  8.19|
# |    |------------------------------------------------|----------|-----|------|
# |    |       0-0.088773|from  to . . . . . . . . . . .|  1781.000| 1781| 24.98|
# |    |0.088773-0.177547|from  to . . . . . . . . . . .|  1611.000| 1611| 22.59|
# |    | 0.177547-0.26632|from  to . . . . . . . . . . .|  2069.000| 2069| 29.01|
# |    | 0.26632-0.355094|from  to . . . . . . . . . . .|  1670.000| 1670| 23.42|
# |-----------------------------------------------------|----------|-----|------|
# |2506|ES-SE                                           |14,006.000|14006| 16.08|
# |    |------------------------------------------------|----------|-----|------|
# |    |       0-0.088773|from  to . . . . . . . . . . .|  3947.000| 3947| 28.18|
# |    |0.088773-0.177547|from  to . . . . . . . . . . .|  1459.000| 1459| 10.42|
# |    | 0.177547-0.26632|from  to . . . . . . . . . . .|  2950.000| 2950| 21.06|
# |    | 0.26632-0.355094|from  to . . . . . . . . . . .|  5650.000| 5650| 40.34|
# |-----------------------------------------------------|----------|-----|------|
# |4539|ES-CO                                           |13,741.000|13741| 15.78|
# |    |------------------------------------------------|----------|-----|------|
# |    |       0-0.088773|from  to . . . . . . . . . . .|  5683.000| 5683| 41.36|
# |    |0.088773-0.177547|from  to . . . . . . . . . . .|  1584.000| 1584| 11.53|
# |    | 0.177547-0.26632|from  to . . . . . . . . . . .|  1807.000| 1807| 13.15|
# |    | 0.26632-0.355094|from  to . . . . . . . . . . .|  4667.000| 4667| 33.96|
# |-----------------------------------------------------|----------|-----|------|
# |4541|ES-J                                            |13,603.000|13603| 15.62|
# |    |------------------------------------------------|----------|-----|------|
# |    |       0-0.088773|from  to . . . . . . . . . . .|  4293.000| 4293| 31.56|
# |    |0.088773-0.177547|from  to . . . . . . . . . . .|  1894.000| 1894| 13.92|
# |    | 0.177547-0.26632|from  to . . . . . . . . . . .|  2270.000| 2270| 16.69|
# |    | 0.26632-0.355094|from  to . . . . . . . . . . .|  5146.000| 5146| 37.83|
# |-----------------------------------------------------------------------------|
# |TOTAL                                                |87,085.000|87085|100.00|
# +-----------------------------------------------------------------------------+

# Colombia
v.proj in=colombia location=latlong mapset=luigi
g.region vect=colombia
# Make some room on the margins
g.region n=n+75000 s=s-200000 e=e+200000 w=w-200000
# Import more vectors based on current region extent
v.proj in=colombia_departments location=latlong mapset=luigi
v.proj in=colombia_cities location=latlong mapset=luigi
# Get a region box for clipping world vectors in latlong location
v.in.region output=colombia_region_box
# Go back to latlong and clip country boundaries and coastline
v.proj in=colombia_region_box location=laea_colombia mapset=medgold
v.select ainput=ne_10m_admin_0_countries_lakes binput=colombia_region_box output=ne_10m_admin_0_countries_lakes_colombia operator=overlap
v.select ainput=ne_10m_coastline binput=colombia_region_box output=ne_10m_coastline_colombia operator=overlap
# Reproject in laea after clipping
v.proj in=ne_10m_admin_0_countries_lakes_colombia location=latlong mapset=luigi
v.proj in=ne_10m_coastline_colombia location=latlong mapset=luigi

# Check extent (actually, the extent is the region) but more
# importantly the resolution of rasters before reprojecting
# rasters
# Crop data

# For rasters, first do region clipping in latlong location
# Rasters with 5 min resolution
g.region rast=coffee_HarvestedAreaFraction
g.region -a vect=colombia_region_box
r.mapcalc "coffee_HarvestedAreaFraction_colombia = coffee_HarvestedAreaFraction"
r.mapcalc "coffee_Production_colombia = coffee_Production"
r.mapcalc "coffee_YieldPerHectare_colombia = coffee_YieldPerHectare"
# Rasters with 1 min resolution
g.region rast=SR_HR
g.region -a vect=colombia_region_box
r.mapcalc "SR_HR_colombia = SR_HR"
r.mapcalc "GRAY_HR_SR_OB_DR_colombia = GRAY_HR_SR_OB_DR"
r.mapcalc "NE1_HR_LC_SR_W_DR.blue_colombia = NE1_HR_LC_SR_W_DR.blue"
r.mapcalc "NE1_HR_LC_SR_W_DR.green_colombia = NE1_HR_LC_SR_W_DR.green"
r.mapcalc "NE1_HR_LC_SR_W_DR.red_colombia = NE1_HR_LC_SR_W_DR.red"
# Rasters with 30 sec resolution
g.region rast=elevation_1KMmd_GMTEDmd
g.region -a vect=colombia_region_box
r.mapcalc "elevation_1KMmd_GMTEDmd_colombia = elevation_1KMmd_GMTEDmd"


# Move to projected location and reproject after getting
# region extent/resolution from source clipped raster
# Rasters with 5 min resolution
r.proj -g input=coffee_Production_colombia location=latlong mapset=luigi
# n=1100444.25412261 s=-1149549.4556994 w=-1185631.25592358 e=891174.40111514 rows=244 cols=227
g.region n=1100444.25412261 s=-1149549.4556994 w=-1185631.25592358 e=891174.40111514 rows=244 cols=227
r.proj input=coffee_Production_colombia location=latlong mapset=luigi
r.proj input=coffee_HarvestedAreaFraction_colombia location=latlong mapset=luigi
r.proj input=coffee_YieldPerHectare_colombia location=latlong mapset=luigi
# Rasters with 1 min resolution
r.proj -g input=SR_HR_colombia location=latlong mapset=luigi
# n=1100413.50331293 s=-1149580.58177944 w=-1180097.56948443 e=889374.03692534 rows=1220 cols=1131
g.region n=1100413.50331293 s=-1149580.58177944 w=-1180097.56948443 e=889374.03692534 rows=1220 cols=1131
r.proj input=SR_HR_colombia location=latlong mapset=luigi
r.proj input=GRAY_HR_SR_OB_DR_colombia location=latlong mapset=luigi
r.proj input=NE1_HR_LC_SR_W_DR.blue_colombia location=latlong mapset=luigi
r.proj input=NE1_HR_LC_SR_W_DR.green_colombia location=latlong mapset=luigi
r.proj input=NE1_HR_LC_SR_W_DR.red_colombia location=latlong mapset=luigi
# Make composite RGB raster
r.composite red=NE1_HR_LC_SR_W_DR.red_colombia green=NE1_HR_LC_SR_W_DR.green_colombia blue=NE1_HR_LC_SR_W_DR.blue_colombia output=NE1_HR_LC_SR_W_DR.composite_colombia
# Rasters with 30 sec resolution
r.proj -g input=elevation_1KMmd_GMTEDmd_colombia location=latlong mapset=luigi  
# n=1099492.85656904 s=-1149585.75536407 w=-1179175.26652435 e=889401.1080394 rows=2439 cols=2261
g.region n=1099492.85656904 s=-1149585.75536407 w=-1179175.26652435 e=889401.1080394 rows=2439 cols=2261
r.proj input=elevation_1KMmd_GMTEDmd_colombia location=latlong mapset=luigi
# Get a labeled raster for area statistics
# (check spatial resolution)
# Colombia
g.region -a res=1000
v.to.rast in=colombia_departments out=colombia_departments use=attr col=cat labelcol=iso_3166_2
# Clip shaded relief
v.to.rast input=ne_10m_admin_0_countries_lakes_colombia output=ne_10m_admin_0_countries_lakes_colombia use=val value=1
r.mapcalc "SR_HR_colombia_clip = if (ne_10m_admin_0_countries_lakes_colombia, SR_HR_colombia, null())"
r.colors map=SR_HR_colombia_clip raster=SR_HR_colombia
r.mapcalc "SR_HR_colombia_clip_inverse = if (isnull(colombia_departments), SR_HR_colombia_clip, null())"
r.colors map=SR_HR_colombia_clip_inverse raster=SR_HR_colombia
#################################################
# Region for the Colombia mapping routine
g.region vect=colombia
# Make some room on the margins
g.region n=n-70000 s=s-50000 e=e+50000 w=w+233000
# Align with resolution
g.region -a res=1000
#################################################
# Test statistics report
r.report -en map=colombia_departments,coffee_HarvestedAreaFraction_colombia units=k,c,p nsteps=4
# +-----------------------------------------------------------------------------+
# |                         RASTER MAP CATEGORY REPORT                          |
# |LOCATION: laea_colombia                              Wed Sep 25 00:19:00 2019|
# |-----------------------------------------------------------------------------|
# |          north:  955000    east:  740000                                    |
# |REGION    south: -999000    west: -716000                                    |
# |          res:      1000    res:     1000                                    |
# |-----------------------------------------------------------------------------|
# |MASK: none                                                                   |
# |-----------------------------------------------------------------------------|
# |MAPS: Rasterized vector map from labels (colombia_departments in medgold)    |
# |        (untitled) (coffee_HarvestedAreaFraction_colombia in medgold)        |
# |-----------------------------------------------------------------------------|
# |               Category Information                |  square  |   cell|   %  |
# |   #|description                                   |kilometers|  count| cover|
# |-----------------------------------------------------------------------------|
# | 772|CO-NAR                                        |    30,259|  30259|  2.68|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    30,259|  30259|100.00|
# |---------------------------------------------------|----------|-------|------|
# | 775|CO-PUT                                        |    25,391|  25391|  2.25|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    25,391|  25391|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1343|CO-CHO                                        |    45,727|  45727|  4.05|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    45,727|  45727|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1350|CO-GUA                                        |    71,201|  71201|  6.30|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    71,201|  71201|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1351|CO-VAU                                        |    51,656|  51656|  4.57|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    51,656|  51656|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1352|CO-AMA                                        |   109,261| 109261|  9.67|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|   109,261| 109261|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1394|CO-LAG                                        |    19,425|  19425|  1.72|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    19,425|  19425|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1395|CO-CES                                        |    22,118|  22118|  1.96|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    22,118|  22118|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1396|CO-NSA                                        |    21,867|  21867|  1.94|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    21,867|  21867|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1399|CO-ARA                                        |    23,790|  23790|  2.11|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    23,790|  23790|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1400|CO-BOY                                        |    22,902|  22902|  2.03|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    22,902|  22902|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1401|CO-VID                                        |    98,540|  98540|  8.72|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    98,540|  98540|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1804|CO-CAU                                        |    30,351|  30351|  2.69|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    29,889|  29889| 98.48|
# |    |0.057167-0.114333|from  to . . . . . . . . . .|       462|    462|  1.52|
# |---------------------------------------------------|----------|-------|------|
# |1816|CO-VAC                                        |    20,531|  20531|  1.82|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    17,353|  17353| 84.52|
# |    |0.057167-0.114333|from  to . . . . . . . . . .|      3038|   3038| 14.80|
# |    |  0.114333-0.1715|from  to . . . . . . . . . .|       140|    140|  0.68|
# |---------------------------------------------------|----------|-------|------|
# |1883|CO-ANT                                        |    63,006|  63006|  5.58|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    63,006|  63006|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1884|CO-COR                                        |    24,865|  24865|  2.20|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    24,865|  24865|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1885|CO-SUC                                        |    10,835|  10835|  0.96|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    10,835|  10835|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1886|CO-BOL                                        |    26,245|  26245|  2.32|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    26,245|  26245|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1887|CO-ATL                                        |      3285|   3285|  0.29|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|      3285|   3285|100.00|
# |---------------------------------------------------|----------|-------|------|
# |1888|CO-MAG                                        |    22,555|  22555|  2.00|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    22,497|  22497| 99.74|
# |    |0.057167-0.114333|from  to . . . . . . . . . .|        58|     58|  0.26|
# |---------------------------------------------------|----------|-------|------|
# |3774|CO-CAQ                                        |    90,061|  90061|  7.97|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    90,061|  90061|100.00|
# |---------------------------------------------------|----------|-------|------|
# |3775|CO-HUI                                        |    19,031|  19031|  1.68|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    19,031|  19031|100.00|
# |---------------------------------------------------|----------|-------|------|
# |3776|CO-GUV                                        |    55,057|  55057|  4.87|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    54,148|  54148| 98.35|
# |    |0.057167-0.114333|from  to . . . . . . . . . .|       909|    909|  1.65|
# |---------------------------------------------------|----------|-------|------|
# |3777|CO-CAL                                        |      7365|   7365|  0.65|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|      7027|   7027| 95.41|
# |    |0.057167-0.114333|from  to . . . . . . . . . .|       328|    328|  4.45|
# |    |  0.114333-0.1715|from  to . . . . . . . . . .|        10|     10|  0.14|
# |---------------------------------------------------|----------|-------|------|
# |3778|CO-CAS                                        |    43,775|  43775|  3.87|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    43,775|  43775|100.00|
# |---------------------------------------------------|----------|-------|------|
# |3779|CO-MET                                        |    86,254|  86254|  7.63|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    86,173|  86173| 99.91|
# |    |0.057167-0.114333|from  to . . . . . . . . . .|        81|     81|  0.09|
# |---------------------------------------------------|----------|-------|------|
# |3780|CO-CUN                                        |      1677|   1677|  0.15|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|      1677|   1677|100.00|
# |---------------------------------------------------|----------|-------|------|
# |3781|CO-SAN                                        |    30,773|  30773|  2.72|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    30,773|  30773|100.00|
# |---------------------------------------------------|----------|-------|------|
# |3782|CO-TOL                                        |    24,019|  24019|  2.13|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    23,344|  23344| 97.19|
# |    |0.057167-0.114333|from  to . . . . . . . . . .|       675|    675|  2.81|
# |---------------------------------------------------|----------|-------|------|
# |3783|CO-QUI                                        |      1896|   1896|  0.17|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|       766|    766| 40.40|
# |    |0.057167-0.114333|from  to . . . . . . . . . .|      1099|   1099| 57.96|
# |    |  0.114333-0.1715|from  to . . . . . . . . . .|        31|     31|  1.64|
# |---------------------------------------------------|----------|-------|------|
# |3784|CO-CUN                                        |    22,640|  22640|  2.00|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|    22,559|  22559| 99.64|
# |    |0.057167-0.114333|from  to . . . . . . . . . .|        81|     81|  0.36|
# |---------------------------------------------------|----------|-------|------|
# |3785|CO-RIS                                        |      3536|   3536|  0.31|
# |    |----------------------------------------------|----------|-------|------|
# |    |       0-0.057167|from  to . . . . . . . . . .|      2514|   2514| 71.10|
# |    |0.057167-0.114333|from  to . . . . . . . . . .|       942|    942| 26.64|
# |    |  0.114333-0.1715|from  to . . . . . . . . . .|        80|     80|  2.26|
# |-----------------------------------------------------------------------------|
# |TOTAL                                              | 1,129,894|1129894|100.00|
# +-----------------------------------------------------------------------------+

# List of map layers in location laea_andalusia
g.list type=rast,vect                                                           
----------------------------------------------
raster files available in mapset <medgold>:
GRAY_HR_SR_OB_DR_andalusia
GRAY_HR_SR_OB_DR_andalusia_250m
NE1_HR_LC_SR_W_DR.blue_andalusia
NE1_HR_LC_SR_W_DR.blue_andalusia_250m
NE1_HR_LC_SR_W_DR.green_andalusia
NE1_HR_LC_SR_W_DR.green_andalusia_250m
NE1_HR_LC_SR_W_DR.red_andalusia
NE1_HR_LC_SR_W_DR.red_andalusia_250m
SR_HR_andalusia
SR_HR_andalusia_250m
SR_HR_andalusia_clip
SR_HR_andalusia_clip_250m
SR_HR_andalusia_clip_inverse
SR_HR_andalusia_clip_inverse_250m
andalusia_provinces
elevation_1KMmd_GMTEDmd_andalusia
ne_10m_admin_0_countries_lakes_andalusia
olive_HarvestedAreaFraction_andalusia
olive_Production_andalusia
olive_YieldPerHectare_andalusia
----------------------------------------------
----------------------------------------------
vector files available in mapset <medgold>:
andalusia
andalusia_cities
andalusia_provinces
andalusia_region_box
ne_10m_admin_0_countries_lakes_andalusia
ne_10m_coastline_andalusia
----------------------------------------------

# List of map layers in location laea_colombia
g.list type=rast,vect
----------------------------------------------
raster files available in mapset <medgold>:
GRAY_HR_SR_OB_DR_colombia               SR_HR_colombia_clip_inverse
NE1_HR_LC_SR_W_DR.blue_colombia         coffee_HarvestedAreaFraction_colombia
NE1_HR_LC_SR_W_DR.composite_colombia    coffee_Production_colombia
NE1_HR_LC_SR_W_DR.green_colombia        coffee_YieldPerHectare_colombia
NE1_HR_LC_SR_W_DR.red_colombia          colombia_departments
SR_HR_colombia                          elevation_1KMmd_GMTEDmd_colombia
SR_HR_colombia_clip                     ne_10m_admin_0_countries_lakes_colombia
----------------------------------------------
----------------------------------------------
vector files available in mapset <medgold>:
colombia                                colombia_region_box
colombia_cities                         ne_10m_admin_0_countries_lakes_colombia
colombia_departments                    ne_10m_coastline_colombia
----------------------------------------------


# Get olive distribution map from PNAS paper 
# https://doi.org/10.1073/pnas.1314437111
# for use in Euro-Mediterranean climate projections in collaboration with JRC
# (e.g., for the policy brief)

# original map info
r.info map=olive_groves_new_raster_masked_below900@luigi                        
#  +----------------------------------------------------------------------------+
#  | Map:      olive_groves_new_raster_maske  Date: Thu Oct 14 18:29:12 2010    |
#  | Mapset:   luigi                          Login of Creator: Luigi           |
#  | Location: AEA_Med                                                          |
#  | DataBase: /Users/luigi/grassdata/                                          |
#  | Title:    olive_groves_new_raster_masked_below900                          |
#  | Timestamp: none                                                            |
#  |----------------------------------------------------------------------------|
#  |                                                                            |
#  |   Type of Map:  raster               Number of Categories: 1               |
#  |   Data Type:    CELL                                                       |
#  |   Rows:         1482                                                       |
#  |   Columns:      1637                                                       |
#  |   Total Cells:  2426034                                                    |
#  |        Projection: Albers Equal Area                                       |
#  |            N:    2562000    S:   -1884000   Res:  3000                     |
#  |            E:    2568000    W:   -2343000   Res:  3000                     |
#  |   Range of data:    min = 1  max = 1                                       |
#  |                                                                            |
#  |   Data Description:                                                        |
#  |    generated by r.mapcalc                                                  |
#  |                                                                            |
#  |   Comments:                                                                |
#  |    if(MedOliveDEM_resamp < 900, olive_groves_new_raster, null())           |
#  |                                                                            |
#  +----------------------------------------------------------------------------+

# calculate where output map will be
r.proj input=olive_groves_new_raster_masked_below900 location=AEA_Med mapset=luigi -p
Source cols: 1637
Source rows: 1482
Local north: 61:28:59.461617N
Local south: 18:01:13.847978N
Local west: 22:22:10.693368W
Local east: 55:32:56.456629E
Input map <olive_groves_new_raster_masked_below900@luigi> in location <AEA_Med>:

# same but in a form which can be cut and pasted into a g.region call
r.proj input=olive_groves_new_raster_masked_below900 location=AEA_Med mapset=luigi -g
# n=61:28:59.461617N s=18:01:13.847978N w=22:22:10.693368W e=55:32:56.456629E rows=1482 cols=1637

# set region for reprojection and print it
g.region n=61:28:59.461617N s=18:01:13.847978N w=22:22:10.693368W e=55:32:56.456629E rows=1482 cols=1637 -p
# projection: 3 (Latitude-Longitude)
# zone:       0
# datum:      wgs84
# ellipsoid:  a=6378137 es=0.00669438
# north:      61:28:59.461617N
# south:      18:01:13.847978N
# west:       22:22:10.693368W
# east:       55:32:56.456629E
# nsres:      0:01:45.577337
# ewres:      0:02:51.354398
# rows:       1482
# cols:       1637
# cells:      2426034

# round resolution to something cleaner
g.region res=0:01 -a -p

# perform the reprojection
r.proj input=olive_groves_new_raster_masked_below900 location=AEA_Med mapset=luigi

# Input:
# Cols: 1637 (1637)
# Rows: 1482 (1482)
# North: 2562000.000000 (2562000.000000)
# South: -1884000.000000 (-1884000.000000)
# West: -2343000.000000 (-2343000.000000)
# East: 2568000.000000 (2568000.000000)
# EW-res: 3000.000000
# NS-res: 3000.000000

# Output:
# Cols: 4673 (4676)
# Rows: 2607 (2608)
# North: 61.483333 (61.483333)
# South: 18.033333 (18.016667)
# West: -22.350000 (-22.383333)
# East: 55.533333 (55.550000)
# EW-res: 0.016667
# NS-res: 0.016667

# Allocating memory and reading input raster map...
# Projecting...
# r.proj complete.

# reprojected map info
r.info map=olive_groves_new_raster_masked_below900@luigi                        
 # +----------------------------------------------------------------------------+
 # | Map:      olive_groves_new_raster_maske  Date: Fri Mar 27 12:50:56 2020    |
 # | Mapset:   luigi                          Login of Creator: luigi           |
 # | Location: latlong                                                          |
 # | DataBase: /Volumes/My Passport/zen_casasGIS                                |
 # | Title:    olive_groves_new_raster_masked_below900                          |
 # | Timestamp: none                                                            |
 # |----------------------------------------------------------------------------|
 # |                                                                            |
 # |   Type of Map:  raster               Number of Categories: 0               |
 # |   Data Type:    CELL                                                       |
 # |   Rows:         2607                                                       |
 # |   Columns:      4673                                                       |
 # |   Total Cells:  12182511                                                   |
 # |        Projection: Latitude-Longitude                                      |
 # |            N:     61:29N    S:     18:02N   Res:  0:01                     |
 # |            E:     55:32E    W:     22:21W   Res:  0:01                     |
 # |   Range of data:    min = 1  max = 1                                       |
 # |                                                                            |
 # |   Data Description:                                                        |
 # |    generated by r.proj                                                     |
 # |                                                                            |
 # |   Comments:                                                                |
 # |    r.proj location="AEA_Med" mapset="luigi" input="olive_groves_new_ras\   |
 # |    ter_masked_below900" method="nearest" memory=300                        |
 # |                                                                            |
 # +----------------------------------------------------------------------------+

# export to geotiff
r.out.gdal input=olive_groves_new_raster_masked_below900@luigi output=/Users/luigi/olive_distribution_pnas.tif format=GTiff
# Checking GDAL data type and nodata value...
# Using GDAL data type <Byte>
# Input raster map contains cells with NULL-value (no-data). The value 255 will be used to represent no-data values in the input map. You can specify a nodata value with the nodata option.
# Exporting raster data to GTiff format...
# r.out.gdal complete. File </Users/luigi/olive_distribution_pnas.tif> created.

# # proj info
# g.proj -j                                                                       
# +proj=longlat
# +no_defs
# +a=6378137
# +rf=298.257223563
# +towgs84=0.000,0.000,0.000 

# # gdalinfo
# gdalinfo /Users/luigi/olive_distribution_pnas.tif
# Driver: GTiff/GeoTIFF
# Files: /Users/luigi/olive_distribution_pnas.tif
# Size is 4676, 2608
# Coordinate System is:
# GEOGCS["WGS 84",
#     DATUM["WGS_1984",
#         SPHEROID["WGS 84",6378137,298.257223563,
#             AUTHORITY["EPSG","7030"]],
#         AUTHORITY["EPSG","6326"]],
#     PRIMEM["Greenwich",0],
#     UNIT["degree",0.0174532925199433],
#     AUTHORITY["EPSG","4326"]]
# Origin = (-22.383333333333333,61.483333333333334)
# Pixel Size = (0.016666666666667,-0.016666666666667)
# Metadata:
#   AREA_OR_POINT=Area
#   TIFFTAG_SOFTWARE=GRASS GIS 7.7.svn with GDAL 2.4.1
# Image Structure Metadata:
#   INTERLEAVE=BAND
# Corner Coordinates:
# Upper Left  ( -22.3833333,  61.4833333) ( 22d23' 0.00"W, 61d29' 0.00"N)
# Lower Left  ( -22.3833333,  18.0166667) ( 22d23' 0.00"W, 18d 1' 0.00"N)
# Upper Right (  55.5500000,  61.4833333) ( 55d33' 0.00"E, 61d29' 0.00"N)
# Lower Right (  55.5500000,  18.0166667) ( 55d33' 0.00"E, 18d 1' 0.00"N)
# Center      (  16.5833333,  39.7500000) ( 16d35' 0.00"E, 39d45' 0.00"N)
# Band 1 Block=4676x1 Type=Byte, ColorInterp=Palette
#   Description = olive_groves_new_raster_masked_below900@luigi
#   NoData Value=255
#   Metadata:
#     COLOR_TABLE_RULES_COUNT=1
#     COLOR_TABLE_RULE_RGB_0=1.000000e+00 1.000000e+00 255 0 0 255 0 0




Things to do:

 - PS driver https://grass.osgeo.org/grass64/manuals/psdriver.html
 - put weather station data and analysis in git
 - import weather station loctions from .\pbdm work med-gold\weather station data andalucia\andalusia_satations_for_import.txt
 - get name of closest agmerra gridcell
 - run daily as done in .\weather station data andalucia\andalusia_stations_analysis\daily_run_andalusia_satations
 - if overall legend for multi year is needed (hard if crop area mask is set), try using only grid cells inside tha crop growing area
 - https://land.copernicus.eu/pan-european/corine-land-cover
