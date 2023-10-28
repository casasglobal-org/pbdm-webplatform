import netCDF4
import os 
import math
import numpy as np

my_latitudes = [42.2000000000027, 42.1000000000027, 42.0000000000027, 
    41.9000000000027, 41.8000000000027, 41.7000000000027, 41.6000000000028, 
    41.5000000000028, 41.4000000000028, 41.3000000000028, 41.2000000000028, 
    41.1000000000028, 41.0000000000028, 40.9000000000028, 40.8000000000028, 
    40.7000000000028, 40.6000000000028, 40.5000000000028, 40.4000000000028, 
    40.3000000000028, 40.2000000000028, 40.1000000000028, 40.0000000000028, 
    39.9000000000028, 39.8000000000029]
my_longitudes = [15.0999999999889, 15.1999999999889, 15.2999999999889, 
    15.3999999999889, 15.4999999999889, 15.5999999999889, 15.6999999999889, 
    15.7999999999889, 15.8999999999889, 15.9999999999889, 16.0999999999889, 
    16.1999999999888, 16.2999999999888, 16.3999999999888, 16.4999999999888, 
    16.5999999999888, 16.6999999999888, 16.7999999999888, 16.8999999999888, 
    16.9999999999888, 17.0999999999888, 17.1999999999888, 17.2999999999888, 
    17.3999999999888, 17.4999999999888, 17.5999999999888, 17.6999999999888, 
    17.7999999999888, 17.8999999999888, 17.9999999999887, 18.0999999999887, 
    18.1999999999887, 18.2999999999887, 18.3999999999887, 18.4999999999887, 
    18.5999999999887, 18.6999999999887]
# myCommand = 'nccopy -k classic {} {}'.format("./Precipitation-Flux_AgERA5_2021.nc","./Precipitation-Flux_AgERA5_1990-classic.nc")
# os.system(myCommand)
variables = netCDF4.MFDataset("./Precipitation-Flux_AgERA5_2021-classic.nc")

# print(variables.variables['Precipitation_Flux'][0,,0])

longitudes = variables.variables['lon'][:].tolist()
latitudes = variables.variables['lat'][:].tolist()


print(longitudes)
new_l = []
longitudes_indexes=[]
for el in longitudes:
    new_l.append('%.13f'%(el))

for el in my_longitudes:
    longitudes_indexes.append(new_l.index('%.13f'%(el)))

new_l = []
latitudes_indexes=[]
for el in latitudes:
    new_l.append('%.13f'%(el))

for el in my_latitudes:
    latitudes_indexes.append(new_l.index('%.13f'%(el)))

print(longitudes_indexes)
print(latitudes_indexes)

couples = []
i = 0 
j = 0 
for lat in latitudes_indexes:
    for lon in longitudes_indexes:
        try:
            if variables.variables['Precipitation_Flux'][0,lat,lon] != '--':
                couples.append((lat, lon, i, j))
                j = j + 1
        except Exception as e:
            print(e)
            pass
    j = 0
    i = i + 1
print(couples)

print(len(longitudes))
print(len(longitudes_indexes))
print(len(latitudes))
print(len(latitudes_indexes))

for el in couples:
    with open("punti.dat", "a")as f:
        f.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format("000000", longitudes_indexes[el[3]], latitudes_indexes[el[2]], '%.1f'%(longitudes[el[1]]), '%.1f'%(latitudes[el[0]]), "ITA", "PUG"))