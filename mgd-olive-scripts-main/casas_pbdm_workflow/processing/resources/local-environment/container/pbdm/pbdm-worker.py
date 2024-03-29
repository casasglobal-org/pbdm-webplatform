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

local_path = "filesystem/pbdm/"
PATH = '/txtfiles/'
NEW_PATH = '/output/'
DAILY_PATH = '/daily/'
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
  print(os.getcwd())
  end_date = os.environ['end_date']
  start_date = os.environ['start_date']
  country = os.environ['country'].replace("-250m", "").replace("-1km", "")
  model = os.environ['model']
  dataset = os.environ['dataset']
  otinterval = os.environ['output_time_interval']
  cwd = os.getcwd()
  resolution = os.environ['resolution']
  #DATASET_PATH = "{}/{}/{}".format(local_path,dataset, country)
  cwd = os.getcwd()
  # if resolution != "": 
  #   coords_file = coords_file.replace(".dat", f"_{resolution}.dat")
  #   if '250m' in resolution:
  #     PATH = PATH.replace('txtfiles/','txtfiles_250m/')
  #   else: 
  #     PATH = PATH.replace('txtfiles/','txtfiles_1km/')
  
  zip_file_name = '{}_{}_{}_{}_{}{}_oti{}.zip'.format(dataset, model, start_date.replace('/', '-'), end_date.replace('/', '-'), country,resolution, otinterval)
  #json_file_name = '{}json/{}_{}_{}_{}_{}.json'.format(SECOND_BUCKET_PATH.format(dataset), dataset, model, start_date.replace('/', '-'), end_date.replace('/', '-'), country)
  # es agmerra/wf/pbdm/json/

  start_date = start_date.split('/')
  start_date = datetime.date(int(start_date[0]), int(start_date[1]),int(start_date[2]))
  end_date = end_date.split('/')
  end_date = datetime.date(int(end_date[0]), int(end_date[1]), int(end_date[2]))


  try:
    # coords file (punti.dat) dovrà trovarsi dentro /dataset/country/
    # reading coords file, value  row   col   lon   lat   country
    list_files = []
    with open("./"+coords_file, 'r') as f:
      print(coords_file)
      for line in f.readlines():
        values = line.replace('\n', '').split('\t')
        if resolution != "":
          list_files.append('{}.txt'.format(values[2]))
        else:
          print(values)
          list_files.append('{}_{}_{}_{}.txt'.format(dataset, values[1], values[2], values[5]))
          
    print(list_files)
    #for each file on output folder
    i = 0
    s = ""
    for file in list_files:
      print("file: ", file)
      # launch command like this -> wine olive_no-w olive.ini 01/01/1990 01/01/2000 file.txt
      cmdCommand ='wine {} {} {} {} {} {}'.format('{}.exe'.format(model), '{}.ini'.format(model), ' {} {} {} '.format(str(start_date.month), str(start_date.day), str(start_date.year)),' {} {} {} '.format(str(end_date.month), str(end_date.day), str(end_date.year)),otinterval, "."+PATH+file)     #specify your cmd command
      print(cmdCommand)
      process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
      process.wait()
      process = subprocess.Popen(cmdCommand.split(), stdout=subprocess.PIPE)
      process.wait()
      i = i + 1
      fd = os.rename('OliveDaily.txt', 'OliveDaily{}.txt'.format(i))
      s = s + 'OliveDaily{}.txt'.format(i)
           
    os.makedirs(cwd+DAILY_PATH, exist_ok=True)
    os.system('type {} > OliveDaily.txt'.format(s))
    for f in os.listdir(cwd):
      if f.startswith("OliveDaily") or f.startswith("OliveSummaries"):
          os.rename(f, cwd+DAILY_PATH+f)
      print(str(datetime.date.today().strftime('%d')))
      if f.startswith("Olive_" + str(datetime.date.today().strftime('%d'))) or f.startswith('Gis'):
        if not os.path.isfile(cwd+DAILY_PATH+f):
          os.rename(f, cwd+DAILY_PATH+f)
    # os.chmod(cwd+DAILY_PATH, 777)
    # for file in os.listdir(cwd+DAILY_PATH):
    #   with zipfile.ZipFile(cwd+DAILY_PATH+zip_file_name, 'a') as myzip:
    #     myzip.write(cwd+DAILY_PATH+file, file)
    # VERIFICA SE NECESSARIO RIMUOVERE I FILE 
  except Exception as e:
    raise e

if __name__ == "__main__":
  polling()