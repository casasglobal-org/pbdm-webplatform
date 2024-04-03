import cdsapi
import datetime
import calendar
import os
import boto3
import logging
import shutil
import zipfile
import subprocess
import xarray as xr
import json

# Configuration of the logger for monitoring execution
logger = logging.getLogger()
logger.setLevel("INFO")

def ensure_directory_exists(directory_path):
    """Ensure the directory exists to avoid FileNotFoundError."""
    os.makedirs(directory_path, exist_ok=True)
    os.chmod(directory_path, 0o775)

def download_and_extract(client, variable, year, month_str, days, label, s3_bucket):
    common_params = {
        'version': '1_1',
        'format': 'zip',
        'variable': variable,
        'year': str(year),
        'month': month_str,
        'day': days
    }

    # Handling of specific_params based on the variable
    if variable == '2m_relative_humidity':
        return process_humidity(client, common_params, year, month_str, label, s3_bucket)

    return {"status": "success", "message": f"Successfully processed and extracted {variable}"}

def process_humidity(client, common_params, year, month_str, label, s3_bucket):
    times = ['06_00', '09_00', '12_00', '15_00', '18_00']
    time_results = []
    
    for time in times:
        try:
            formatted_time = time.split('_')[0] + 'h'
            extract_to = f"/tmp/{label}-2m-{formatted_time}"
            ensure_directory_exists(extract_to)  # Ensure directory exists
            file_name = f"{extract_to}-{year}-{month_str}.zip"
            specific_params = {'time': time}
            response = client.retrieve('sis-agrometeorological-indicators', {**common_params, **specific_params})
            response.download(target=file_name)
            extract_files(file_name, extract_to)
            output_file_path = merge_nc_files(extract_to, output_filename=f"{label}-2m-{formatted_time}-{year}-{month_str}-merged.nc")
            upload_to_s3(output_file_path, s3_bucket, year, label, formatted_time)
            logger.info(f"Successfully processed and extracted 2m_relative_humidity for {month_str}-{year} at {formatted_time}")
            time_results.append({"time": formatted_time, "status": "success", "message": "Success"})
        except Exception as e:
            logger.error(f"Error processing 2m_relative_humidity for {month_str}-{year} at {formatted_time}: {e}", exc_info=True)
            time_results.append({"time": formatted_time, "status": "error", "message": str(e)})

    return time_results

def extract_files(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def merge_nc_files(extract_to, output_filename):
    """
    Tenta di replicare la funzionalità cdo mergetime unendo i file .nc lungo la dimensione temporale.

    :param extract_to: Directory che contiene i file .nc da unire.
    :param output_filename: Nome del file .nc risultante dal merge.
    """
    # Costruisci il percorso completo del file di output
    output_file_path = os.path.join(extract_to, output_filename)
    
    # Raccogli tutti i file .nc nella directory specificata
    nc_files = sorted([os.path.join(extract_to, f) for f in os.listdir(extract_to) if f.endswith('.nc')])
    
    if not nc_files:
        logger.info("No .nc files found to merge in the directory: " + extract_to)
        return None  # Se non ci sono file .nc, termina la funzione
    
    datasets = []  # Inizializza la lista dei dataset per gestire correttamente il blocco finally

    try:
        # Apre i dataset individualmente
        datasets = [xr.open_dataset(nc_file, engine='netcdf4') for nc_file in nc_files]
        
        # Concatena i dataset lungo la dimensione temporale
        combined_ds = xr.concat(datasets, dim='time', data_vars='minimal', coords='minimal', compat='override')
        
        # Salva il dataset combinato come un nuovo file .nc
        combined_ds.to_netcdf(output_file_path)

        logger.info(f"Files merged successfully into {output_file_path}")
    except Exception as e:
        logger.error(f"Failed to merge .nc files with xarray: {e}")
        # Assicurati di rilanciare l'eccezione per segnalare il fallimento
        raise
    finally:
        # Assicura la chiusura di tutti i dataset aperti
        for ds in datasets:
            ds.close()

    return output_file_path  # Ritorna il percorso del file unito

def upload_to_s3(output_file_path, s3_bucket, year, label, formatted_time):
    """
    Uploads the specified file to an S3 bucket.

    :param output_file_path: Path del file da caricare.
    :param bucket_name: Nome del bucket S3 dove caricare il file.
    :param year: Anno da usare nella struttura della chiave S3.
    :param month_str: Mese da usare nella struttura della chiave S3.
    :param file_label: Etichetta da usare nella struttura della chiave S3.
    """
    s3 = boto3.client('s3')
    file_name = os.path.basename(output_file_path)
    s3_key = f"AgERA5/raw/{year}/{label}-2m-{formatted_time}/Monthly/{file_name}"

    try:
        s3.upload_file(output_file_path, s3_bucket, s3_key)
        logger.info(f"Uploaded {file_name} to S3 bucket {s3_bucket} at {s3_key}")
    except Exception as e:
        logger.error(f"Failed to upload {file_name} to S3: {e}")

def lambda_handler(event, context):
    api_key = os.getenv('CDS_API_KEY')
    api_url = os.getenv('CDS_API_URL')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    client = cdsapi.Client(url=api_url, key=api_key)

    try:
        today = datetime.date.today()
        previous_month = today.month - 1 or 12
        year = today.year if today.month > 1 else today.year - 1
        month_str = f"{previous_month:02d}"
        days = [f"{day:02d}" for day in range(1, calendar.monthrange(year, previous_month)[1] + 1)]

        variable = '2m_relative_humidity'
        label = 'Relative-Humidity'
        time_results = download_and_extract(client, variable, year, month_str, days, label, s3_bucket)

        # Calcolo di success_count e error_count basato sui risultati di 'time'
        success_count = sum(1 for result in time_results if result.get('status') == 'success')
        error_count = len(time_results) - success_count
        logger.info(f"Preparing summary with success_count: {success_count}, error_count: {error_count}")
        summary = f"Processing completed with {success_count} successes and {error_count} errors."
        logger.info(summary)
        
        # Modifica qui per corrispondere alla struttura di output attesa dalla State Machine
        status_code = 200 if error_count == 0 else 500
        status_message = "SUCCESS" if error_count == 0 else "FAILURE"

        # Restituisce la risposta
        return {
            "statusCode": status_code,
            "body": json.dumps({  # Usa json.dumps per serializzare il dizionario in una stringa JSON
                "Payload": {
                    "Status": status_message,
                    "Message": summary
                }
            })
        }

    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({  # Usa json.dumps per serializzare il dizionario in una stringa JSON
                "Payload": {
                    "Status": "FAILURE",
                    "Message": f"An error occurred: {str(e)}"
                }
            })
        }
