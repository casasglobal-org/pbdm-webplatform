import boto3
import os
import botocore
import subprocess
import zipfile
from datetime import date
import json
import datetime
import time 
import botocore
from botocore.exceptions import ClientError
import shutil  
sqs = boto3.client('sqs',region_name='eu-west-1')
queue_url = 'https://sqs.eu-west-1.amazonaws.com/662713783319/dev-pbdm-ti-workflow'

os.system("set AWS_DEFAULT_REGION=eu-west-1")

s3 = boto3.resource(
  "s3", 
  region_name='eu-west-1'
  )
s3Client = boto3.client(
  's3', region_name='eu-west-1'
  )
BUCKET_NAME = 'dev-pbdm-workflow'
SECOND_BUCKET_NAME = 'data.pbdm.it'
bucket = s3.Bucket(BUCKET_NAME)
bucket2 = s3.Bucket(SECOND_BUCKET_NAME)
dynamodb = boto3.resource(
  'dynamodb',
  region_name='eu-west-1'
  )
PATH = "\\txtfiles\\"
NEW_PATH = "\\output\\"
DAILY_PATH = '\\daily\\'
# conterrà dataset e country
DATASET_PATH = "\{}\{}"
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


def remove_files(cwd, DATASET_PATH, NEW_PATH):
  
  #remove files
  rm_files = [f for f in os.listdir(cwd+DATASET_PATH+NEW_PATH)]
  for f in rm_files:
    os.remove(cwd+DATASET_PATH+NEW_PATH+f) 
  
  #remove files
  rm_files2 = [f for f in os.listdir(cwd+DATASET_PATH+DAILY_PATH)]
  for f in rm_files2:
    os.remove(cwd+DATASET_PATH+DAILY_PATH+f)

def start_threads(threads):
    for x in threads:
        x.start()

    for x in threads:
        x.join()

def polling(message):
  global coords_file
  global PATH
  global DATASET_PATH
  requestId = message['requestId']
  end_date = message['end_date']
  start_date = message['start_date']
  country = '-'.join(message['country'].split('-')[0:2])
  model = message['model']
  dataset = message['dataset']
  wf = message['wf']
  resolution = message['resolution']
  DATASET_PATH = "\{}\{}".format(dataset, country)
  otinterval = message['output_time_interval']
  cwd = os.getcwd()
  if resolution != "": 
    coords_file = coords_file.replace(".dat", f"_{resolution}.dat")
    if '250m' in resolution:
      PATH = PATH.replace('txtfiles\\','txtfiles_250m\\')
    else: 
      PATH = PATH.replace('txtfiles\\','txtfiles_1km\\')

  zip_file_name = '{}_{}_{}_{}_{}.zip'.format(dataset, model, start_date.replace('/', '-'), end_date.replace('/', '-'), country)
  #json_file_name = '{}json/{}_{}_{}_{}_{}.json'.format(SECOND_BUCKET_PATH.format(dataset), dataset, model, start_date.replace('/', '-'), end_date.replace('/', '-'), country)
  # es agmerra/wf/pbdm/json/
  json_file_name = '{}json/{}.json'.format(SECOND_BUCKET_PATH.format(dataset, wf), requestId)

  start_date = start_date.split('/')
  start_date = datetime.date(int(start_date[0]), int(start_date[1]),int(start_date[2]))
  end_date = end_date.split('/')
  end_date = datetime.date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
  print("qui entra")

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
          # coords file (punti.dat) dovrà trovarsi dentro /dataset/country/
          # reading coords file, value  row   col   lon   lat   country
          print(cwd+DATASET_PATH+"\\"+coords_file)
          with open(cwd+DATASET_PATH+"\\"+coords_file, 'r') as f:
            for line in f.readlines():
              values = line.replace('\n', '').split('\t')
              name = '{}_{}_{}_{}.txt'.format(dataset, values[1], values[2], values[5])
              # creating file agmerra for selected point (lat, lon) and saving it on txtfiles folder
              #values[5].split('-')[0]
              if resolution != "":
                file_name = '{}{}.txt'.format(cwd+DATASET_PATH+PATH, values[2])
                newfile_name = '{}{}.txt'.format(cwd+DATASET_PATH+NEW_PATH, values[2])

              else:
                file_name = '{}_{}_{}_{}.txt'.format(cwd+DATASET_PATH+PATH+dataset, values[1], values[2],values[5].split('-')[0])
                newfile_name = '{}_{}_{}_{}.txt'.format(cwd+DATASET_PATH+NEW_PATH+dataset, values[1], values[2], values[5])
              
              # if file doesn't exists in local, download it from s3
              if not os.path.isfile(file_name):
                try:
                  # downloading file from s3 and saving it on txtfiles folder 
                  bucket.download_file(FIRST_BUCKET_PATH.format(dataset)+name, file_name)
                except botocore.exceptions.ClientError as e:
                  if e.response['Error']['Code'] == "404":
                    pass
              #i = 0
              # opening file AGmerra in txtfiles folder
              with open(file_name, 'r') as file:
                # creating newfile_name on output folder
                with open(newfile_name, 'w',newline='\r' ) as newf:
                  lines = file.readlines()
                  print(len(lines))
                  newf.write(lines[0])
                  newf.write(lines[1])
                  newf.write(lines[2])
                  days = start_date-datetime.date(date[dataset][country],1,1)
                  diff = end_date-start_date
                  print(newfile_name)
                  print(days.days+3)
                  print(days.days+diff.days+4)
                  for n in range(days.days+3, days.days+diff.days+4):
                    print(n)
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
          return e
          #raise
        
        #rm_files = [f for f in os.listdir(cwd+PATH)]
        #for f in rm_files:
        #  os.remove(cwd+PATH+f)

        requestId = message['requestId']
        #for each file on output folder
        i = 0
        s = ""
        commands = []
        for file in os.listdir(cwd+DATASET_PATH+NEW_PATH):
          # launch command like this -> wine olive_no-w olive.ini 01/01/1990 01/01/2000 file.txt
          cmdCommand ='{} {} {} {} {} {}'.format('.\{}_no-w.exe'.format(model), '.\{}.ini'.format(model), ' {} {} {} '.format(str(start_date.month), str(start_date.day), str(start_date.year)),' {} {} {} '.format(str(end_date.month), str(end_date.day), str(end_date.year)),otinterval, cwd+DATASET_PATH+NEW_PATH+file)     #specify your cmd command
         
          print(cmdCommand)
          process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
          try:
            process.wait()
          except subprocess.TimeoutExpired:
            process.kill()
          i = i + 1
          fd = os.rename('OliveDaily.txt', 'OliveDaily{}.txt'.format(i))
          #shutil.move('OliveDaily{}.txt'.format(i), os.path.join(cwd, 'OliveDaily{}.txt'.format(i)))
          s = s + 'OliveDaily{}.txt'.format(i)
          #os.system('del OliveDaily.txt')
          
        
        os.system('type {} > OliveDaily.txt'.format(s))
        #cwd = '/filesystem/{}/'.format(requestId)
        for f in os.listdir(cwd):
          if f.startswith("OliveDaily") or f.startswith("OliveSummaries"):
              os.rename(f, cwd+DATASET_PATH+DAILY_PATH+f)
          print(str(datetime.date.today().strftime('%d')))
          if f.startswith("Olive_" + str(datetime.date.today().strftime('%d'))) or f.startswith('Gis'):
            if not os.path.isfile(cwd+DATASET_PATH+DAILY_PATH+f):
              os.rename(f, cwd+DATASET_PATH+DAILY_PATH+f)
        os.chmod(cwd+DATASET_PATH+DAILY_PATH, 777)
        for file in os.listdir(cwd+DATASET_PATH+DAILY_PATH):
          with zipfile.ZipFile(cwd+DATASET_PATH+DAILY_PATH+zip_file_name, 'a') as myzip:
            myzip.write(cwd+DATASET_PATH+DAILY_PATH+file, '{}/'.format(wf)+file)
        # VERIFICA SE NECESSARIO RIMUOVERE I FILE 
        bucket2.upload_file(cwd+DATASET_PATH+DAILY_PATH+zip_file_name, SECOND_BUCKET_PATH.format(dataset) + zip_file_name)
        object = s3.Bucket(SECOND_BUCKET_NAME).Object(SECOND_BUCKET_PATH.format(dataset) + zip_file_name)
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
        print('esce qui')
        remove_files(cwd, DATASET_PATH, NEW_PATH)
        #raise
        return e
        
  remove_files(cwd, DATASET_PATH, NEW_PATH)
  

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
    while True:
        messages = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=20
        )
        if 'Messages' in messages.keys():
            message = json.loads(messages['Messages'][0]['Body'])
            receipt_handler = messages['Messages'][0]['ReceiptHandle']
            print("dopo loads")
            print(message)
            res = polling(message)
            print(res)
            break
            if res == 'done':
                response = sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt_handler
                )
                print(response)
