import boto3
import os
import botocore
import subprocess
import zipfile
from datetime import date
import json
import datetime
from botocore.exceptions import ClientError


s3 = boto3.resource(
  "s3"
  )
s3Client = boto3.client(
  's3'
  )
BUCKET_NAME = os.environ['BUCKET_NAME'] #dev-data.med-gold.eu-tf
bucket = s3.Bucket(BUCKET_NAME)
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
  "agmerra": 1980,
  "AgERA5": 1979
}


def start_threads(threads):
    for x in threads:
        x.start()

    for x in threads:
        x.join()

def polling():
  requestId = os.environ['requestId']
  end_date = os.environ['end_date']
  start_date = os.environ['start_date']
  country = os.environ['country']
  model = os.environ['model']
  dataset = os.environ['dataset']
  wf = os.environ['wf']
  otinterval = os.environ['output_time_interval']
  cwd = os.getcwd()
  zip_file_name = '{}_{}_{}_{}_{}.zip'.format(dataset, model, start_date.replace('/', '-'), end_date.replace('/', '-'), country)
  json_file_name = '{}json/{}_{}_{}_{}_{}.json'.format(SECOND_BUCKET_PATH.format(dataset), dataset, model, start_date.replace('/', '-'), end_date.replace('/', '-'), country)

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
          print('qui entra')
          # reading coords file, value  row   col   lon   lat   country
          with open(coords_file, 'r') as f:
            for line in f.readlines():
              values = line.replace('\n', '').split('\t')
              print(values)
              name = '{}_{}_{}_{}.txt'.format(dataset, values[1], values[2], values[5])
              # creating file agmerra for selected point (lat, lon) and saving it on txtfiles folder
              #values[5].split('-')[0]
              file_name = '.{}_{}_{}_{}.txt'.format(PATH+dataset, values[1], values[2],values[5].split('-')[0])
              # if file doesn't exists in local, download it from s3
              if not os.path.isfile(file_name):
                try:
                  # downloading file from s3 and saving it on txtfiles folder 
                  bucket.download_file(FIRST_BUCKET_PATH.format(dataset)+name, file_name)
                except botocore.exceptions.ClientError as e:
                  if e.response['Error']['Code'] == "404":
                    pass
              # newfile_name is file cut, that contain variables for each day between start_year and end_year, saved on output folder
              newfile_name = '.{}_{}_{}_{}.txt'.format(NEW_PATH+dataset, values[1], values[2], values[5])
              #i = 0
              # opening file AGmerra in txtfiles folder
              with open(file_name, 'r') as file:
                # creating newfile_name on output folder
                with open(newfile_name, 'w',newline='\r' ) as newf:
                  lines = file.readlines()
                  newf.write(lines[0])
                  newf.write(lines[1])
                  newf.write(lines[2])
                  days = start_date-datetime.date(date[dataset],1,1)
                  diff = end_date-start_date
                  print(newfile_name)
                  for n in range(days.days+3, days.days+diff.days+4):
                    newf.write(lines[n])
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
          raise
        
        rm_files = [f for f in os.listdir(cwd+PATH)]
        for f in rm_files:
          os.remove(cwd+PATH+f)

        requestId = os.environ['requestId']
        #for each file on output folder
        i = 0
        s = ""
        commands = []
        for file in os.listdir(cwd+NEW_PATH):
          # launch command like this -> wine olive_no-w olive.ini 01/01/1990 01/01/2000 file.txt
          cmdCommand ='wine {} {} {} {} {} {}'.format('./{}.exe'.format(model), './{}.ini'.format(model), ' {} {} {} '.format(str(start_date.month), str(start_date.day), str(start_date.year)),' {} {} {} '.format(str(end_date.month), str(end_date.day), str(end_date.year)),otinterval, cwd+NEW_PATH+file)     #specify your cmd command
         
          print(cmdCommand)
          process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
          #commands.append(process)
          process.wait()
          # process2 = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
          # process2.wait()
          os.system("ls")
          i = i + 1
          os.rename('OliveDaily.txt', 'OliveDaily{}.txt'.format(i))
          #shutil.move('OliveDaily{}.txt'.format(i), os.path.join(cwd, 'OliveDaily{}.txt'.format(i)))
          s = s + 'OliveDaily{}.txt'.format(i)
          #os.close('OliveDaily{}.txt'.format(i))
        
        os.system('cat {} > OliveDaily.txt'.format(s))
        #cwd = '/filesystem/{}/'.format(requestId)
        for f in os.listdir(cwd):
          if f.startswith("OliveDaily.txt") or f.startswith("OliveSummaries"):
              os.rename(f, cwd+DAILY_PATH+f)
          print(str(datetime.date.today().strftime('%d')))
          if f.startswith("Olive_" + str(datetime.date.today().strftime('%d'))) or f.startswith('Gis'):
            if not os.path.isfile(cwd+DAILY_PATH+f):
              os.rename(f, cwd+DAILY_PATH+f)
        os.chmod(cwd+DAILY_PATH, 777)
        for file in os.listdir(cwd+DAILY_PATH):
          with zipfile.ZipFile(cwd+DAILY_PATH+zip_file_name, 'a') as myzip:
            myzip.write(cwd+DAILY_PATH+file, '{}/'.format(wf)+file)
        
        bucket.upload_file(cwd+DAILY_PATH+zip_file_name, SECOND_BUCKET_PATH.format(dataset) + zip_file_name)
        object = s3.Bucket(BUCKET_NAME).Object(SECOND_BUCKET_PATH.format(dataset) + zip_file_name)
        object.Acl().put(ACL='public-read')
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
        raise
  
  #remove files
  rm_files = [f for f in os.listdir(cwd+NEW_PATH)]
  for f in rm_files:
    os.remove(cwd+NEW_PATH+f) 
  
  #remove files
  rm_files2 = [f for f in os.listdir(cwd+DAILY_PATH)]
  for f in rm_files2:
    os.remove(cwd+DAILY_PATH+f)
  
  #url= '{}/{}/{}'.format('https://s3-eu-west-1.amazonaws.com', BUCKET_NAME, SECOND_BUCKET_PATH + zip_file_name)

  try:
        s3Client.get_object(Bucket=BUCKET_NAME, Key="{}/wf/{}/".format(dataset, wf) + zip_file_name)
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
      exit(404)


if __name__ == '__main__':
  polling()
