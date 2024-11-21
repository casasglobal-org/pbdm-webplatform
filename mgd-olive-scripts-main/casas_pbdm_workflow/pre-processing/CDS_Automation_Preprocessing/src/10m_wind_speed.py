import os
import cdsapi
import boto3
import uuid
import datetime
import calendar
import logging
import zipfile
import xarray as xr

# Configurazione del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        # URL e API Key per l'accesso al servizio Copernicus
        url = os.environ.get('CDS_API_URL', 'https://cds.climate.copernicus.eu/api')  # URL di default se non impostato
        key = os.environ.get('CDS_API_KEY')  # Assicurati di impostare questa variabile d'ambiente
        # Inizializza il client CDS API
        client = cdsapi.Client(url=url, key=key)

        # Calcola il mese e l'anno precedenti
        today = datetime.date.today()
        previous_month = today.month - 1 or 12
        year = today.year if today.month > 1 else today.year - 1
        month_str = f"{previous_month:02d}"

        # Ottiene tutti i giorni del mese precedente
        days_in_month = calendar.monthrange(year, previous_month)[1]
        days = [f"{day:02d}" for day in range(1, days_in_month + 1)]

        # Definisci il dataset e i parametri della richiesta
        dataset = "sis-agrometeorological-indicators"
        request = {
            "format": "zip",
            "variable": "10m_wind_speed",
            "statistic": "24_hour_mean",
            "year": str(year),
            "month": month_str,
            "day": days,
            "version": "1_1"
        }

        # Percorso temporaneo per il file scaricato
        statistic = "24_hour_mean"
        label = "Wind-Speed-10m-Mean"
        extract_to = f"/tmp/{label}"
        os.makedirs(extract_to, exist_ok=True)
        zip_file = f"{extract_to}/{year}-{month_str}.zip"

        # Scarica i dati e salva nel file zip temporaneo
        logger.info("Downloading data from CDS...")
        result = client.retrieve(dataset, request)
        result.download(target=zip_file)
        logger.info("Download completed.")

        # Estrai i file dal zip
        logger.info("Extracting files...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logger.info("Extraction completed.")

        # Unisci i file NetCDF utilizzando xarray
        logger.info("Merging NetCDF files...")
        nc_files = sorted([os.path.join(extract_to, f) for f in os.listdir(extract_to) if f.endswith('.nc')])

        if not nc_files:
            raise Exception("No NetCDF files found after extraction.")

        datasets = [xr.open_dataset(nc_file) for nc_file in nc_files]
        combined_ds = xr.concat(datasets, dim='time')
        merged_file = f"{extract_to}/{label}-{year}-{month_str}-merged.nc"
        combined_ds.to_netcdf(merged_file)

        # Chiudi i dataset aperti
        for ds in datasets:
            ds.close()

        logger.info("Merge completed.")

        # Configurazione per il caricamento su S3
        s3 = boto3.client('s3')
        bucket_name = os.environ.get('S3_BUCKET_NAME')
        s3_key = f"AgERA5/raw/{year}/{label}/Monthly/{os.path.basename(merged_file)}"

        # Carica il file su S3
        logger.info("Uploading merged file to S3...")
        s3.upload_file(merged_file, bucket_name, s3_key)
        logger.info(f"File uploaded to s3://{bucket_name}/{s3_key}")

        # Rimuovi i file temporanei
        logger.info("Cleaning up temporary files...")
        os.remove(zip_file)
        os.remove(merged_file)
        for nc_file in nc_files:
            os.remove(nc_file)
        os.rmdir(extract_to)
        logger.info("Cleanup completed.")

        return {
            'statusCode': 200,
            'body': f"Dati scaricati, uniti e caricati con successo su s3://{bucket_name}/{s3_key}"
        }

    except Exception as e:
        # Log dell'errore
        logger.error(f"Si è verificato un errore: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': f"Si è verificato un errore: {e}"
        }
