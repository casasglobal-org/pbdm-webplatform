from netCDF4 import Dataset
from threading import Thread
from datetime import date
import netCDF4
import datetime
import calendar
import sys
import os
import boto3
import botocore
import xarray as xr
import multiprocessing as mp
import datetime
import time

BASE_FILE_NAME = "{}/{}/Andalusia/"
FILE_NAME = "AgERA5_{0}_{1}.nc"
FILE_KEYS = ['Temperature-Air-2m-Max-24h', 'Temperature-Air-2m-Min-24h','Solar-Radiation-Flux','Precipitation-Flux','Relative-Humidity-2m-06h', 'Relative-Humidity-2m-09h','Relative-Humidity-2m-12h','Relative-Humidity-2m-15h','Relative-Humidity-2m-18h','Wind-Speed-10m-Mean']
KEYS = ['Temperature-Air-2m-Max-24h', 'Temperature-Air-2m-Min-24h','Solar-Radiation-Flux','Precipitation-Flux','Relative-Humidity','Wind-Speed-10m-Mean']
RU_KEYS = ['Relative-Humidity-2m-06h', 'Relative-Humidity-2m-09h','Relative-Humidity-2m-12h','Relative-Humidity-2m-15h','Relative-Humidity-2m-18h']
COLS = ['MO', 'DA', 'YEAR', 'TMAX', 'TMIN', 'SOL', 'PRCP', 'RH', 'WIND']
DIRECTORY = 'output'
START_YEAR = 1979
END_YEAR = 2022
BUCKET_PATH = 'AgERA5/raw/'
PATH = "/output/"
NC4_PATH='nc4/'
BUCKET_NAME = 'data.med-gold.eu'
s3 = boto3.resource("s3",region_name='eu-west-1')
s3Client = boto3.client('s3')
bucket = s3.Bucket(BUCKET_NAME)
threads = []

longitudes = [15.0, 15.1, 15.2, 
    15.3, 15.4, 15.5, 15.6, 
    15.7, 15.8, 15.9, 16.0, 
    16.1, 16.2, 16.3, 16.4, 
    16.5, 16.6, 16.7, 16.8, 
    16.9, 17.0, 17.1, 17.2, 
    17.3, 17.4, 17.5, 17.6, 
    17.7, 17.8, 17.9, 18.0, 
    18.1, 18.2, 18.3, 18.4, 
    18.5, 18.6]

latitudes = [42.2, 42.1, 42.0, 
    41.9, 41.8, 41.7, 41.6, 
    41.5, 41.4, 41.3, 41.2, 
    41.1, 41.0, 40.9, 40.8, 
    40.7, 40.6, 40.5, 40.4, 
    40.3, 40.2, 40.1, 40.0, 
    39.9, 39.8]

def import_data(start_year, end_year):
    nasa_data = {}
    print(start_year)
    print(end_year)
    for year in range(start_year, end_year+1):
        print(year)
        variables = {}
        for k in FILE_KEYS:
            cwd = os.getcwd()
            name_of_file = ""
            # try:
            #     variables[k] = Dataset(cwd+'/'+NC4_PATH+name_of_file, "r")
            # except Exception as e:
            try:
                print(BUCKET_PATH+BASE_FILE_NAME.format(year, k))
                objs = bucket.objects.filter(Delimiter = '/', Prefix =BUCKET_PATH+BASE_FILE_NAME.format(year, k))
                size = sum(1 for obj in objs)
                list_of_file = []
                for obj in objs:
                    name_of_file = obj.key.split('/')[-1]
                    if 'nc' in name_of_file:
                        bucket.download_file(obj.key, cwd+'/'+NC4_PATH+name_of_file)
                        myCommand = 'nccopy -k classic {} {}'.format(cwd+'/'+NC4_PATH+name_of_file.replace('_C3S-glob-agric', '_new'),cwd+'/'+NC4_PATH+name_of_file.replace('_C3S-glob-agric', '_new').replace('_new',''))
                        os.system(myCommand)
                        list_of_file.append(cwd+'/'+NC4_PATH+name_of_file.replace('_C3S-glob-agric', '_new').replace('_new',''))
                        # os.remove(NC4_PATH+name_of_file)
                        # os.remove(NC4_PATH+name_of_file.replace('_C3S-glob-agric', '_new'))
                variables[k] = netCDF4.MFDataset(list_of_file)
                for f in list_of_file:
                    os.remove(f)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist.")
                else:
                    raise
        nasa_data[year] = (variables)
    return nasa_data

def gen_file(data, file_name, col, row, lon, lat, country, start_year, end_year):
    with open(file_name, 'a') as f:
        print('Generating {}...'+ file_name)
        if not os.path.isfile(file_name):
            f.write('{}\n'.format(file_name[3+len(DIRECTORY):]))
            f.write('{}\t{}\n'.format(lon, lat))
            f.write('{}\n'.format('\t'.join(COLS)))
        s = []
        for year in range(start_year, end_year+1):
            c_date = datetime.date(year,1,1)
            ordinal = c_date.toordinal()
            i = 0
            value = 0
            while(True):
                min_ru = 10000
                try:
                    for k in KEYS:
                        if 'Solar-Radiation-Flux' in k:
                            value = data[year][k].variables[k.replace('-', '_')][i, latitudes.index(float(lat)), longitudes.index(float(lon))]
                            # conversion from J m^-2 day^-1 to W m^-2
                            s.append('{:.1f}'.format(value/86400))
                        else:
                            if 'Temperature-Air-2m-Max-24h' in k or 'Temperature-Air-2m-Min-24h'in k:
                                value = data[year][k].variables[k.replace('-', '_')][i, latitudes.index(float(lat)), longitudes.index(float(lon))]
                                if value != 0:
                                    s.append('{:.1f}'.format(value-273.15))
                                else:
                                    s.append('{:.1f}'.format(value))
                            else:
                                if 'Relative-Humidity' in k:
                                    for r in RU_KEYS:
                                        value = data[year][r].variables[r.replace('-', '_')][i, latitudes.index(float(lat)), longitudes.index(float(lon))]
                                        if value < min_ru:
                                            min_ru = value
                                    s.append('{:.1f}'.format(min_ru))
                                else:
                                    value = data[year][k].variables[k.replace('-', '_')][i, latitudes.index(float(lat)), longitudes.index(float(lon))]
                                    s.append('{:.1f}'.format(value))
                    date = datetime.date.fromordinal(ordinal+i)
                    f.write('{:02d}\t{:02d}\t{}\t{}\n\r'.format(date.month, date.day, year, '\t'.join(s)))
                    i = i + 1
                    s = []
                except ValueError:
                    break

def start_threads(threads):
    for x in threads:
        time.sleep(2)
        x.start()

    for x in threads:
        time.sleep(2)
        x.join()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(sys.argv)
        print('python worker.py input_file_name start_year end_year')
    else:
        print(longitudes.index(-7.2))
        cwd = os.getcwd()
        data = import_data(int(sys.argv[2]), int(sys.argv[3]))
        coords_file = sys.argv[1]
        with open(coords_file, 'r') as f:
            for line in f.readlines():
                values = line.split('\t')
                file_name = './{}/AgERA5_{}_{}_{}.txt'.format(DIRECTORY, values[1], values[2], values[5].replace('\n', ''))
                print(file_name)
                gen_file(data, file_name, int(values[1])-1, int(values[2])-1, values[3], values[4], values[5].replace('\n', ''), int(sys.argv[2]), int(sys.argv[3]))