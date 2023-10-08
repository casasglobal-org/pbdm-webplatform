from netCDF4 import Dataset
import datetime
from datetime import date
import calendar
import sys
import os
import boto3 
import botocore
import multiprocessing as mp
from threading import Thread
import datetime
import time


BASE_FILE_NAME = "AgMERRA_{0}_{1}.nc4"
KEYS = ['tmax', 'tmin', 'srad', 'prate', 'rhstmax', 'wndspd']
COLS = ['MO', 'DA', 'YEAR', 'TMAX', 'TMIN', 'SOL', 'PRCP', 'RH', 'WIND']
DIRECTORY = 'output'
START_YEAR = 1980
END_YEAR = 2010
BUCKET_PATH = 'agmerra/raw/'
PATH = "/output/"
NC4_PATH='nc4/'
BUCKET_NAME = 'dev-pbdm-workflow'
s3 = boto3.resource("s3",region_name='eu-west-1')
s3Client = boto3.client('s3')
bucket = s3.Bucket(BUCKET_NAME)
threads = []

def import_data(start_year, end_year):
    nasa_data = {}
    for year in range(start_year, end_year+1):
        variables = {}
        for k in KEYS:
            cwd = os.getcwd()
            try:
                variables[k] = Dataset(cwd+'/'+NC4_PATH+BASE_FILE_NAME.format(year, k), "r")
            except Exception as e:
                try:
                    bucket.download_file(BUCKET_PATH+str(year)+'/'+BASE_FILE_NAME.format(year, k), cwd+'/'+NC4_PATH+BASE_FILE_NAME.format(year, k))
                    variables[k] = Dataset(cwd+'/'+NC4_PATH+BASE_FILE_NAME.format(year, k), "r")
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        print("The object does not exist.")
                    else:
                        raise
        nasa_data[year] = (variables)

    return nasa_data
        


def gen_file(data, file_name, col, row, lon, lat, country, start_year, end_year):
    with open(file_name, 'w') as f:
        print('Generating {}...'+ file_name)
        f.write('{}\n'.format(file_name[3+len(DIRECTORY):]))
        f.write('{}\t{}\n'.format(lon, lat))
        f.write('{}\n'.format('\t'.join(COLS)))
        s = []
        for year in range(start_year, end_year+1):
            c_date = datetime.date(year,1,1)
            ordinal = c_date.toordinal()
            i = 0
            while(True):
                try:
                    print(i)
                    for k in KEYS:
                        if k == 'srad':
                            # conversion from MJ m^-2 day^-1 to W m^-2
                            s.append('{:.1f}'.format(data[year][k].variables[k][i, row, col]/ 0.0864))
                        else:
                            s.append('{:.1f}'.format(data[year][k].variables[k][i, row, col]))
                    date = datetime.date.fromordinal(ordinal+i) 
                    f.write('{:02d}\t{:02d}\t{}\t{}\n\r'.format(date.month, date.day, year, '\t'.join(s)))
                    i = i + 1
                    s = []
                except IndexError:
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
        print('python agmerra_review.py input_file_name start_year end_year')
    else:
        cwd = os.getcwd()
        data = import_data(int(sys.argv[2]), int(sys.argv[3]))
        print(data)      
        coords_file = sys.argv[1]
        with open(coords_file, 'r') as f:
            for line in f.readlines():
                values = line.split('\t')
                print(values)
                file_name = './{}/agmerra_{}_{}_{}.txt'.format(DIRECTORY, values[1], values[2], values[5])
                
                if not os.path.isfile(file_name):
                    gen_file(data,file_name,int(values[1])-1, int(values[2])-1, values[3], values[4], values[5], int(sys.argv[2]), int(sys.argv[3]))
                
                '''
                if not os.path.isfile(file_name):
                    thread = Thread(target = gen_file, args =(data,file_name,values[1], values[2], values[3], values[4], values[5], int(sys.argv[2]), int(sys.argv[3]),))
                    threads.append(thread)
                if len(threads) == 2:
                    start_threads(threads)
                '''
