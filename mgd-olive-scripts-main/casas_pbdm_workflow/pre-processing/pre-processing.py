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
FILE_NAME = "AgERA5_{0}_{1}.nc4"
FILE_KEYS = ['Temperature-Air-2m-Max-24h', 'Temperature-Air-2m-Min-24h','Solar-Radiation-Flux','Precipitation-Flux','Relative-Humidity-2m-06h', 'Relative-Humidity-2m-09h','Relative-Humidity-2m-12h','Relative-Humidity-2m-15h','Relative-Humidity-2m-18h','Wind-Speed-10m-Mean']
KEYS = ['Temperature-Air-2m-Max-24h', 'Temperature-Air-2m-Min-24h','Solar-Radiation-Flux','Precipitation-Flux','Relative-Humidity','Wind-Speed-10m-Mean']
RU_KEYS = ['Relative-Humidity-2m-06h', 'Relative-Humidity-2m-09h','Relative-Humidity-2m-12h','Relative-Humidity-2m-15h','Relative-Humidity-2m-18h']
COLS = ['MO', 'DA', 'YEAR', 'TMAX', 'TMIN', 'SOL', 'PRCP', 'RH', 'WIND']
DIRECTORY = 'output'
START_YEAR = 1979
END_YEAR = 2018
BUCKET_PATH = 'AgERA5/raw/'
PATH = "/output/"
NC4_PATH='nc4/'
BUCKET_NAME = 'dev-pbdm-workflow'
s3 = boto3.resource("s3",region_name='eu-west-1')
s3Client = boto3.client('s3')
bucket = s3.Bucket(BUCKET_NAME)
threads = []
latitudes = [38.7,38.6,
    38.5, 38.4, 38.3, 38.2,
    38.1, 38.0, 37.9,
    37.8, 37.7, 37.6, 37.5,
    37.4, 37.3, 37.2, 37.1,
    37.0, 36.9, 36.8, 36.7,
    36.6, 36.5, 36.4, 36.3,
    36.2, 36.1, 36.0, 35.9,
    35.8, 35.7, 35.6, 35.5,
    35.4, 35.3, 35.2, 35.1,
    35.0]
longitudes = [-7.5, -7.4, -7.3, -7.2,
    -7.1, -7.0, -6.9,
    -6.8, -6.7, -6.6,
    -6.5, -6.4, -6.3,
    -6.2, -6.1, -6.0,
    -5.9, -5.8, -5.7, -5.6,
    -5.5, -5.4, -5.3,
    -5.2, -5.1, -5.0,
    -4.9, -4.8, -4.7,
    -4.6, -4.5, -4.4,
    -4.3, -4.2, -4.1, -4.0,
    -3.9, -3.8, -3.7,
    -3.6, -3.5, -3.4,
    -3.3, -3.2, -3.1,
    -3.0, -2.9, -2.8,
    -2.7, -2.6, -2.5,
    -2.4, -2.3, -2.2, -2.1,
    -2.0, -1.9, -1.8, -1.7]

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