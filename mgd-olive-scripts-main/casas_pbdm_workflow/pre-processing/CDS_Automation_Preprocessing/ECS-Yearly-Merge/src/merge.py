import os
import subprocess
import boto3
from datetime import datetime

# Configura i parametri iniziali
current_year = datetime.now().year - 1
bucket = 'dev-pbdm-workflow' #'tebaka-download-testbucket'

# Lista delle variabili da processare
VARIABLES = [
    'Precipitation-Flux', 'Relative-Humidity-2m-06h', 'Relative-Humidity-2m-09h',
    'Relative-Humidity-2m-12h', 'Relative-Humidity-2m-15h', 'Relative-Humidity-2m-18h',
    'Solar-Radiation-Flux', 'Temperature-Air-2m-Max-24h', 'Temperature-Air-2m-Min-24h',
    'Wind-Speed-10m-Mean'
]

def download_from_s3(bucket, variable, year):
    """Scarica tutti i file .nc rilevanti dal bucket S3 per un dato prefisso."""
    s3 = boto3.client('s3')
    downloaded_files = []
    prefix = f"AgERA5/raw/{year}/{variable}/Monthly"
    print(f"Iniziando il download da S3 con prefisso: {prefix}")  # Debug: Stampa il prefisso usato per il download

    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
    
    for page in page_iterator:
        if 'Contents' not in page:
            print("Nessun contenuto trovato per il prefisso specificato.")  # Debug: Nessun file trovato
            break
        
        for obj in page.get('Contents', []):
            key = obj['Key']
            if key.endswith('.nc'):
                filename = key.split('/')[-1]
                print(f"Trovato file .nc: {filename}")  # Debug: Stampa i nomi dei file trovati prima del download
                
                s3.download_file(Bucket=bucket, Key=key, Filename=filename)
                downloaded_files.append(filename)
                print(f"Downloaded {filename}")  # Conferma di download completato
                
    if not downloaded_files:
        print("Nessun file .nc scaricato. Verificare il prefisso e i permessi del bucket.")  # Debug: Nessun download completato
        
    return downloaded_files


def compress_file(input_filename):
    """Comprime il file NetCDF specificato."""
    compressed_filename = f"{input_filename.split('.')[0]}-compressed.nc"
    cmd = ['cdo', '-f', 'nc4c', '-z', 'zip', 'copy', input_filename, compressed_filename]
    subprocess.run(cmd, check=True)
    print(f"Compressed file created: {compressed_filename}")
    return compressed_filename

def merge_files(variable, files, year):
    """Esegue cdo mergetime sui file .nc specificati e li comprime."""
    output_filename = f'{variable}_AgERA5_{year}.nc'
    if files:
        merge_cmd = ['cdo', 'mergetime'] + files + [output_filename]
        subprocess.run(merge_cmd, check=True)
        print(f"Merged file created: {output_filename}")
        
        # Comprimi il file merged
        compressed_output_filename = compress_file(output_filename)
        
        # Calcola e stampa la dimensione del file compresso
        file_size = os.path.getsize(compressed_output_filename)
        print(f"Size of {compressed_output_filename}: {file_size} bytes")
        
        return compressed_output_filename
    else:
        print("No relevant .nc files found for merging.")
        return None

def upload_to_s3(bucket, variable, file_name, year):
    """Carica il file specificato su S3."""
    s3 = boto3.client('s3')
    if file_name:
        key = f"AgERA5/raw/all/{variable}/Global/{file_name}"
        s3.upload_file(Filename=file_name, Bucket=bucket, Key=key)
        print(f"Uploaded {file_name} to {key}")

def clean_up(files):
    """Elimina i file specificati dal file system locale."""
    for file in files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted {file} from local filesystem.")

def process_variable(bucket, variable, year):
    """Processa una singola variabile: scarica, fonde, comprime e carica i file .nc."""
    downloaded_files = download_from_s3(bucket, variable, year)
    if downloaded_files:
        compressed_output_filename = merge_files(variable, downloaded_files, year)
        final_output_filename = compressed_output_filename.replace('-compressed', '')
        
        # Se il nome del file finale è diverso da quello compresso, rinominalo
        if compressed_output_filename != final_output_filename:
            os.rename(compressed_output_filename, final_output_filename)
        
        # Ora carica il file con il nuovo nome, che non ha il suffisso '-compressed'
        if final_output_filename:
            upload_to_s3(bucket, variable, final_output_filename, year)
        
        # Pulisci i file scaricati e il file finale dal filesystem locale
        files_to_clean = downloaded_files + [final_output_filename]
        clean_up(files_to_clean)


def main():
    for variable in VARIABLES:
        process_variable(bucket, variable, current_year)

if __name__ == "__main__":
    main()

