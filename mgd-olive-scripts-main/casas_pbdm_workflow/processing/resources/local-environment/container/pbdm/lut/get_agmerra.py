from netCDF4 import Dataset
import datetime
from datetime import date
import calendar
import sys
import os
import boto3 
import botocore


BASE_FILE_NAME = "AgMERRA_{0}_{1}.nc4"
KEYS = ['tmax', 'tmin', 'srad', 'prate', 'rhstmax', 'wndspd']
COLS = ['MO', 'DA', 'YEAR', 'TMAX', 'TMIN', 'SOL', 'PRCP', 'RH', 'WIND']
DIRECTORY = 'output'
START_YEAR = 1980
END_YEAR = 2010
BUCKET_PATH = 'agmerra/o/'
PATH = '\\output\\'
NC4_PATH='nc4\\'
BUCKET_NAME = 'data.med-gold.eu'
s3 = boto3.resource("s3",region_name='eu-west-1')
s3Client = boto3.client('s3')
bucket = s3.Bucket(BUCKET_NAME)


def import_data(year):
    nasa_data = {}
    for k in KEYS:
        cwd = os.getcwd()
        try:
            nasa_data[k] = Dataset(cwd+'\\'+NC4_PATH+BASE_FILE_NAME.format(year, k), "r")
        except Exception as e:
            try:
                bucket.download_file(BUCKET_PATH+str(year)+'/'+BASE_FILE_NAME.format(year, k), cwd+'\\'+NC4_PATH+BASE_FILE_NAME.format(year, k))
                nasa_data[k] = Dataset(cwd+'\\'+NC4_PATH+BASE_FILE_NAME.format(year, k), "r")
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("The object does not exist.")
                else:
                    raise

    
    return nasa_data


def parse_input_file(input_file, limit):
    coords = []

    if limit > 0:
        for i in range(limit):
            line = input_file.readline()
            values = line.split('\t')
            coords.append((int(values[1]), int(values[2]), float(values[3]), float(values[4]), values[5]))
    else:
        for line in input_file:
            values = line.split('\t')
            coords.append((int(values[1]), int(values[2]), float(values[3]), float(values[4]), values[5]))

    return coords


# coords_file -> file containing a list of pairs of coordinates
# limit -> number of lines which need to be read from file
def generate_txt(coords_file, limit, start_date, end_date):
    start = datetime.datetime.now()
    coords = None

    start_date = start_date.split('/')
    end_date = end_date.split('/')
    start_year = int(start_date[2])
    end_year = int(end_date[2])
    start_month = int(start_date[0])
    end_month = int(end_date[0])
    start_day = int(start_date[1])
    end_day = int(end_date[1])


    print('Retrieving coordinates...')
    # open coordinates file
    with open(coords_file, 'r') as f:

        # parse values from file
        coords = parse_input_file(f, limit)

    print('Generating output files...')
    for year in range(start_year, end_year+1):
        # for every pair of coordinates generate one file
        for col, row, lon, lat, country in coords:
            file_name = './{}/agmerra_{}_{}_{}.txt'.format(DIRECTORY, col, row, country)

            # if file does not exist, create it and write column names
            try:
                with open(file_name, 'r') as f:
                    print('Appending')
                #print('Appending {} data to {}...'+ year+ file_name)
            except IOError:
                # check if output directory exists
                try:
                    os.stat(DIRECTORY)
                except:
                    os.mkdir(DIRECTORY)

                with open(file_name, 'w') as f:
                    print('Generating {}...'+ file_name)
                    f.write('{}\n'.format(file_name[3+len(DIRECTORY):]))
                    f.write('{}\t{}\n'.format(lon, lat))
                    f.write('{}\n'.format('\t'.join(COLS)))

            # append year data
            with open(file_name, 'a') as f:
                try:
                    # import netCDF dataset for current year
                    data = import_data(year)
                    if year == start_year:
                        end = (datetime.date(year,12, 31)-datetime.date(year,start_month, start_day)).days
                    elif year == end_year:
                        end = (datetime.date(year,end_month,end_day)- datetime.date(year,1, 1)).days
                    else:
                        end = 365

                    if calendar.isleap(year):
                        print(year)
                        end = end + 1

                    print(end)
                    for i in range(end):
                        date = (datetime.datetime(year, 1, 1) + datetime.timedelta(i))
                        # retrieve data from netCDF
                        s = []
                        for k in KEYS:
                            if k == 'srad':
                                # conversion from MJ m^-2 day^-1 to W m^-2
                                s.append('{:.1f}'.format(data[k].variables[k][i, row, col]/ 0.0864))
                            else:
                                s.append('{:.1f}'.format(data[k].variables[k][i, row, col]))

                        # print data to file
                        f.write('{:02d}\t{:02d}\t{}\t{}\n'.format(date.month, date.day, date.year, '\t'.join(s)))
                except Exception as e:
                    raise
    print('Done in {}'.format(datetime.datetime.now() - start))

    return


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print(sys.argv)
        print('''python get_agmerra.py input_file_name limit start_date end_date''')
    else:
        generate_txt(sys.argv[1], int(sys.argv[2]),sys.argv[3],sys.argv[4])