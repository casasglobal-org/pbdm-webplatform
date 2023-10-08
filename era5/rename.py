import os
import zipfile
import boto3 

BUCKET_NAME = 'dev-pbdm-workflow'
s3 = boto3.resource("s3",region_name='eu-west-1')
bucket = s3.Bucket(BUCKET_NAME)

locations =[
    {"location":"Andalusia", "coords":
        {"min_lat":"35.1",
        "max_lat":"38.8",
        "min_lon":"-1.8",
        "max_lon":"-7.6"}},
    {"location":"Puglia", 
    "coords":{
    "min_lat":"39.8",
    "max_lat":"42.3",
    "min_lon":"18.7",
    "max_lon":"15.0"}}]

def merge(variable, name):
    filename = ""
    for year in range(1979, 2024):
        folder = "agera5_"+variable+"_all_"+str(year)
        for file in os.listdir(folder):
            filename = file
            break
        os.chdir(folder)
        myCommand = 'cdo mergetime *.nc {}.nc'.format(name+"_AgERA5_"+ str(year))
        print(myCommand)
        os.system(myCommand)
        for file in os.listdir("."):
            if "C3S-glob-agric" in file:
                os.remove(file)
        os.chdir("..")

def extract(variable):
    for file in os.listdir(f"./agera5_{variable}"):
        if ".zip" in file:
            #file = "Temperature-Air-2m-Min-24h_1979_1.zip"
            year = file.split("_")[1]
            #month = file.split("_")[2].replace(".zip", "")
            cartella_destinazione = f"agera5_{variable}"

            # Estrai il contenuto del file ZIP nella cartella di destinazione
            print(os.getcwd())
            print(file.split("_"))
            with zipfile.ZipFile(os.getcwd()+"/"+f"agera5_{variable}/"+file, 'r') as zip_ref:
                zip_ref.extractall(f"agera5_{variable}_all_"+year)

if __name__ == '__main__':
    name = "Precipitation-Flux"
    #extract("prec_flux")
    #merge("prec_flux",name)
    location = "Global"
    for dir in os.listdir("./"):
        if "all" in dir:
            print(dir)
            os.chdir(dir)
            for file in os.listdir("./"):
                if ".nc" in file:
                    for el in locations:
                        exists = False
                        try:
                            os.mkdir(el['location'])
                            myCommand = 'cdo -sellonlatbox,{},{},{},{} {} {}'.format(el['coords']['max_lon'], el['coords']['min_lon'], el['coords']['max_lat'], el['coords']['min_lat'], file, f"./{el['location']}/"+file)
                            os.system(myCommand)
                            year = dir.split("_")[4]
                            print("AgERA5/raw/{}/{}/{}/{}".format(year, name, el['location'],file))
                            bucket.upload_file(f"./{el['location']}/"+file, "AgERA5/raw/{}/{}/{}/{}".format(year, name, el['location'],file))
                        except Exception as e:
                            exists = True
                            print(e)
            if ".nc" in file and not exists:  
                year = dir.split("_")[3]
                bucket.upload_file(file, "AgERA5/raw/{}/{}/{}/{}".format(year, name, "Global",file))
            os.chdir("..")




