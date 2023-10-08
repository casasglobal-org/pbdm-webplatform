import cdsapi
import os
import zipfile
import boto3
import botocore

c = cdsapi.Client()
##BOTO##
s3 = boto3.resource("s3")
s3Client = boto3.client('s3')
BUCKET_NAME= 'dev-pbdm-workflow'
bucket = s3.Bucket(BUCKET_NAME)
FIRST_BUCKET_PATH = 'AgERA5/raw/{}/{}/{}/'
BASE_FILE_NAME = "{}/{}/"
FILE_NAME = "AgERA5_{0}_{1}.nc4"
FILE_KEYS = ['Temperature-Air-2m-Max-24h', 'Temperature-Air-2m-Min-24h','Solar-Radiation-Flux','Precipitation-Flux','Relative-Humidity-2m-06h', 'Relative-Humidity-2m-09h','Relative-Humidity-2m-12h','Relative-Humidity-2m-15h','Relative-Humidity-2m-18h','Wind-Speed-10m-Mean']
KEYS = ['Temperature-Air-2m-Max-24h', 'Temperature-Air-2m-Min-24h','Solar-Radiation-Flux','','Relative-Humidity','Wind-Speed-10m-Mean']
# FILE_KEYS = ['Temperature-Air-2m-Max-24h']
RU_KEYS = ['Relative-Humidity-2m-06h', 'Relative-Humidity-2m-09h','Relative-Humidity-2m-12h','Relative-Humidity-2m-15h','Relative-Humidity-2m-18h']
COLS = ['MO', 'DA', 'YEAR', 'TMAX', 'TMIN', 'SOL', 'PRCP', 'RH', 'WIND']
DIRECTORY = 'output'
START_YEAR = 1979
END_YEAR = 2018
BUCKET_PATH = 'AgERA5/raw/'
PATH = "/output/"
'nc4/'
BUCKET_NAME = 'dev-pbdm-workflow'
s3 = boto3.resource("s3",region_name='eu-west-1')
s3Client = boto3.client('s3')
bucket = s3.Bucket(BUCKET_NAME)
# min_lat = "35.0"
# max_lat = "38.7"
# min_lon = "-1.7"
# max_lon = "-7.5"

min_lat = "39.7"
max_lat = "42.3"
min_lon = "-15"
max_lon = "-18.6"
cwd = os.getcwd()

for year in range(1979, 2018):
    for k in FILE_KEYS:
        cwd = os.getcwd()
        name_of_file = ""
        try:
            print(BUCKET_PATH+BASE_FILE_NAME.format(year, k))
            objs = bucket.objects.filter(Delimiter = '/', Prefix =BUCKET_PATH+BASE_FILE_NAME.format(year, k))
            size = sum(1 for obj in objs)
            list_of_file = []
            for obj in objs:
                name_of_file = obj.key.split('/')[-1]
                if 'nc' in name_of_file:
                    folder = name_of_file.split('_')[0]
                    bucket.download_file(obj.key, cwd+'/'+name_of_file)
                    myCommand = 'cdo -sellonlatbox,{},{},{},{} {} {}'.format(max_lon, min_lon, max_lat, min_lat, cwd+'/'+name_of_file,cwd+'/'+name_of_file.replace('_C3S-glob-agric', '_new'))
                    os.system(myCommand)
                    myCommand = 'nccopy -k classic {} {}'.format(cwd+'/'+name_of_file.replace('_C3S-glob-agric', '_new'),cwd+'/'+name_of_file.replace('_C3S-glob-agric', '_new').replace('_new',''))
                    os.system(myCommand)
                    list_of_file.append(cwd+'/'+name_of_file.replace('_C3S-glob-agric', '_new').replace('_new',''))
                    os.remove(name_of_file)
                    os.remove(name_of_file.replace('_C3S-glob-agric', '_new'))
                    bucket.upload_file(cwd+'/'+name_of_file.replace('_C3S-glob-agric', '_new').replace('_new',''), FIRST_BUCKET_PATH.format(year,folder,'Puglia')+name_of_file.replace('_C3S-glob-agric', '_new').replace('_new',''))
                    print('uploaded')
                    object = s3.Bucket(BUCKET_NAME).Object(FIRST_BUCKET_PATH.format(year,folder,'Puglia')+name_of_file.replace('_C3S-glob-agric', '_new').replace('_new',''))
                    #object.Acl().put(ACL='public-read')
                    os.remove(name_of_file.replace('_C3S-glob-agric', '_new').replace('_new',''))
            for f in list_of_file:
                os.remove(f)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise
