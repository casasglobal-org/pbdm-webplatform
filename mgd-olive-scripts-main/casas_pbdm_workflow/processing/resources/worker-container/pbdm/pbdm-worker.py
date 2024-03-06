import boto3
import os
import botocore
import subprocess
import zipfile
from datetime import date
import json
import datetime
import botocore
from botocore.exceptions import ClientError

os.system(f"set AWS_DEFAULT_REGION={os.environ['REGION']}")

s3 = boto3.resource("s3")
s3Client = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME'] #dev-data.med-gold.eu-tf
bucket = s3.Bucket(BUCKET_NAME)
SECOND_BUCKET_NAME = os.environ['SECOND_BUCKET_NAME'] #dev-data.med-gold.eu-tf
bucket2 = s3.Bucket(SECOND_BUCKET_NAME)
dynamodb = boto3.resource(
  'dynamodb',
  region_name=os.environ['REGION']
  )
PATH = '/txtfiles/'
NEW_PATH = '/output/'
DAILY_PATH = '/daily/'
# bucket path in ordine di chiamata
FIRST_BUCKET_PATH = "{}/p/"
SECOND_BUCKET_PATH = "{}/wf/pbdm/"
coords_file = 'punti.dat'
header_lenght = 3

date = {
  "agmerra": {
    "ESP-AN": 1980},
  "AgERA5": {
      "ESP-AN": 1979,
      "ITA-PUG": 2003
  }
}


def remove_files(cwd, NEW_PATH):
  #remove files
  rm_files = [f for f in os.listdir(cwd+NEW_PATH)]
  for f in rm_files:
    os.remove(cwd+NEW_PATH+f) 
  
  #remove files
  rm_files2 = [f for f in os.listdir(cwd+DAILY_PATH)]
  for f in rm_files2:
    os.remove(cwd+DAILY_PATH+f)

def polling():
  global coords_file
  global PATH
  global DATASET_PATH
  print(os.getcwd())
  requestId = os.environ['requestId']
  end_date = os.environ['end_date']
  start_date = os.environ['start_date']
  country = os.environ['country'].replace("-250m", "").replace("-1km", "")
  model = os.environ['model']
  dataset = os.environ['dataset']
  wf = os.environ['wf']
  otinterval = os.environ['output_time_interval']
  cwd = os.getcwd()
  resolution = os.environ['resolution']
  DATASET_PATH = "filesystem/pbdm/{}/{}".format(dataset, country)
  cwd = os.getcwd()
  if resolution != "": 
    coords_file = coords_file.replace(".dat", f"_{resolution}.dat")
    if '250m' in resolution:
      PATH = PATH.replace('txtfiles/','txtfiles_250m/')
    else: 
      PATH = PATH.replace('txtfiles/','txtfiles_1km/')

  zip_file_name = '{}_{}_{}_{}_{}{}_oti{}.zip'.format(dataset, model, start_date.replace('/', '-'), end_date.replace('/', '-'), country,resolution, otinterval)
  #json_file_name = '{}json/{}_{}_{}_{}_{}.json'.format(SECOND_BUCKET_PATH.format(dataset), dataset, model, start_date.replace('/', '-'), end_date.replace('/', '-'), country)
  # es agmerra/wf/pbdm/json/
  json_file_name = '{}json/{}.json'.format(SECOND_BUCKET_PATH.format(dataset, wf), requestId)

  start_date = start_date.split('/')
  start_date = datetime.date(int(start_date[0]), int(start_date[1]),int(start_date[2]))
  end_date = end_date.split('/')
  end_date = datetime.date(int(end_date[0]), int(end_date[1]), int(end_date[2]))

  try:
    data = {
        "state": "working",
        "requestId": requestId
    }
    s3Client.put_object(
      Body=json.dumps(data),
      Bucket=BUCKET_NAME,
      ContentType='application/json',
      Key=json_file_name
    )
    s3.Object(BUCKET_NAME, SECOND_BUCKET_PATH.format(dataset)+zip_file_name).load()
  except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] != "404":
      print(e)
    else:
      try:
        try:
          # coords file (punti.dat) dovrà trovarsi dentro /dataset/country/
          # reading coords file, value  row   col   lon   lat   country
          print("/"+DATASET_PATH+"/"+coords_file)
          list_files = []
          with open("/"+DATASET_PATH+"/"+coords_file, 'r') as f:
            print("/"+DATASET_PATH+"/"+coords_file)
            for line in f.readlines():
              values = line.replace('\n', '').split('\t')
              name = '{}_{}_{}_{}.txt'.format(dataset, values[1], values[2], values[5])
              # creating file agmerra for selected point (lat, lon) and saving it on txtfiles folder
              #values[5].split('-')[0]
              if resolution != "":
                file_name = '{}{}.txt'.format("/"+DATASET_PATH+PATH, values[2])
                list_files.append('{}.txt'.format(values[2]))
              else:
                file_name = '{}_{}_{}_{}.txt'.format("/"+DATASET_PATH+PATH+dataset, values[1], values[2],values[5].split('-')[0])
                list_files.append('{}_{}_{}.txt'.format(values[1], values[2], values[5]))
              
              # if file doesn't exists in local, download it from s3
              if not os.path.isfile(file_name):
                try:
                  # downloading file from s3 and saving it on txtfiles folder 
                  bucket.download_file(FIRST_BUCKET_PATH.format(dataset)+name, file_name)
                except botocore.exceptions.ClientError as e:
                  if e.response['Error']['Code'] == "404":
                    pass
        except Exception as e:
          data = {
            "state": "failed",
            "requestId": requestId
          }
          s3Client.put_object(
            Body=json.dumps(data),
            Bucket=BUCKET_NAME,
            ContentType='application/json',
            Key=json_file_name
          )
          print(e)
          return e
          #raise
        
        requestId = os.environ['requestId']
        #for each file on output folder
        i = 0
        s = ""
        commands = []
        for file in list_files:
          print("file: ", file)
          # launch command like this -> wine olive_no-w olive.ini 01/01/1990 01/01/2000 file.txt
          cmdCommand ='wine {} {} {} {} {} {}'.format('{}.exe'.format(model), '{}.ini'.format(model), ' {} {} {} '.format(str(start_date.month), str(start_date.day), str(start_date.year)),' {} {} {} '.format(str(end_date.month), str(end_date.day), str(end_date.year)),otinterval, "/"+DATASET_PATH+PATH+file)     #specify your cmd command
          print(cmdCommand)
          # print(cmdCommand)
          process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
          #commands.append(process)
          process.wait()
          process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
          #commands.append(process)
          process.wait()
          i = i + 1
          fd = os.rename('OliveDaily.txt', 'OliveDaily{}.txt'.format(i))
          s = s + 'OliveDaily{}.txt'.format(i)          
        
        os.system('type {} > OliveDaily.txt'.format(s))
        for f in os.listdir(cwd):
          if f.startswith("OliveDaily") or f.startswith("OliveSummaries"):
              os.rename(f, cwd+DAILY_PATH+f)
          print(str(datetime.date.today().strftime('%d')))
          if f.startswith("Olive_" + str(datetime.date.today().strftime('%d'))) or f.startswith('Gis'):
            if not os.path.isfile(cwd+DAILY_PATH+f):
              os.rename(f, cwd+DAILY_PATH+f)
        os.chmod(cwd+DAILY_PATH, 777)
        for file in os.listdir(cwd+DAILY_PATH):
          with zipfile.ZipFile(cwd+DAILY_PATH+zip_file_name, 'a') as myzip:
            myzip.write(cwd+DAILY_PATH+file, '{}/'.format(wf)+file)
        # VERIFICA SE NECESSARIO RIMUOVERE I FILE 
        bucket2.upload_file(cwd+DAILY_PATH+zip_file_name, SECOND_BUCKET_PATH.format(dataset) + zip_file_name)
        object = s3.Bucket(SECOND_BUCKET_NAME).Object(SECOND_BUCKET_PATH.format(dataset) + zip_file_name)
        object.Acl().put(ACL='public-read')
        list_files = []
      except Exception as e:
        data = {
          "state": "failed",
          "requestId": requestId
        }
        s3Client.put_object(
          Body=json.dumps(data),
          Bucket=BUCKET_NAME,
          ContentType='application/json',
          Key=json_file_name
        )
        print('esce qui')
        #remove_files(cwd, DATASET_PATH, NEW_PATH)
        #raise
        return e
        
  #remove_files(cwd, DATASET_PATH, NEW_PATH)
  

  try:
        print(zip_file_name)
        print(BUCKET_NAME)
        s3Client.get_object(Bucket=SECOND_BUCKET_NAME, Key="{}/wf/{}/".format(dataset, wf) + zip_file_name)
        
        data = {
          "state": "done",
          "url": f"http://{SECOND_BUCKET_NAME}.s3.eu-west-1.amazonaws.com/"+ "{}/wf/{}/".format(dataset, wf) + zip_file_name
        }
        s3Client.put_object(
          Body=json.dumps(data),
          Bucket=BUCKET_NAME,
          ContentType='application/json',
          Key=json_file_name
        )
        return "done"
  except ClientError as e:
    if e.response['Error']['Code'] == 'NoSuchKey':
      data = {
        "state": "failed",
        "requestId": requestId
      }
      s3Client.put_object(
        Body=json.dumps(data),
        Bucket=BUCKET_NAME,
        ContentType='application/json',
        Key=json_file_name
      )
    return e

if __name__ == "__main__":
  polling()