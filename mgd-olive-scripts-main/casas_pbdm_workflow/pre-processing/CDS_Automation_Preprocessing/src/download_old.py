import cdsapi
import datetime
import calendar
import os
import boto3
import logging
import shutil
import zipfile

# Configuration of the logger for execution monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_and_upload_to_s3(c, variable, current_year, previous_month_str, days, s3_bucket, file_label):
    # Initialize the S3 client
    s3 = boto3.client('s3')
    # Define common parameters for data retrieval
    common_params = {
        'version': '1_1',
        'format': 'zip',
        'variable': variable,
        'year': str(current_year),
        'month': previous_month_str,
        'day': days
    }

    try:
        if variable == '2m_relative_humidity':
            for time in ['06_00', '09_00', '12_00', '15_00', '18_00']:
                formatted_time = time.replace('_00', 'h')
                specific_file_label = f"{file_label}-2m-{formatted_time}"
                file_name = f"/tmp/{specific_file_label}-{current_year}-{previous_month_str}.zip"
                specific_params = {'time': time}
                response = c.retrieve('sis-agrometeorological-indicators', {**common_params, **specific_params})
                response.download(target=file_name)
                upload_to_s3(s3, file_name, s3_bucket, current_year, previous_month_str, specific_file_label)

        elif variable == '2m_temperature':
            for statistic in ['24_hour_maximum', '24_hour_minimum']:
                specific_file_label = f"{file_label}-{statistic}"
                file_name = f"/tmp/{specific_file_label}-{current_year}-{previous_month_str}.zip"
                specific_params = {'statistic': statistic}
                response = c.retrieve('sis-agrometeorological-indicators', {**common_params, **specific_params})
                response.download(target=file_name)
                upload_to_s3(s3, file_name, s3_bucket, current_year, previous_month_str, specific_file_label)

        elif variable in ['10m_wind_speed', '2m_dewpoint_temperature']:
            statistic = '24_hour_mean'
            specific_file_label = f"{file_label}-{statistic}"
            file_name = f"/tmp/{specific_file_label}-{current_year}-{previous_month_str}.zip"
            specific_params = {'statistic': statistic}
            response = c.retrieve('sis-agrometeorological-indicators', {**common_params, **specific_params})
            response.download(target=file_name)
            upload_to_s3(s3, file_name, s3_bucket, current_year, previous_month_str, specific_file_label)

        else:
            file_name = f"/tmp/{file_label}-{current_year}-{previous_month_str}.zip"
            response = c.retrieve('sis-agrometeorological-indicators', common_params)
            response.download(target=file_name)
            upload_to_s3(s3, file_name, s3_bucket, current_year, previous_month_str, file_label)

        logger.info(f"Successfully processed and uploaded {variable} for {previous_month_str}-{current_year}")
        return {"status": "success", "message": f"Successfully processed and uploaded {variable}"}

    except Exception as e:
        logger.error(f"Error processing {variable}: {e}")
        return {"status": "error", "message": f"Error processing {variable}: {e}"}

def unzip_file(zip_path, extract_to):
    """Extract files from a ZIP archive."""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def upload_to_s3(s3, file_path, bucket_name, current_year, previous_month_str, file_label):
    """Upload extracted files to S3 and clean up the temporary directory."""
    try:
        temp_extract_dir = f"/tmp/extracted_{file_label}"
        os.makedirs(temp_extract_dir, exist_ok=True)
        unzip_file(file_path, temp_extract_dir)

        for extracted_file in os.listdir(temp_extract_dir):
            extracted_file_path = os.path.join(temp_extract_dir, extracted_file)
            s3_key = f"{current_year}/{file_label}/{previous_month_str}/Global/{extracted_file}"
            with open(extracted_file_path, 'rb') as file_data:
                s3.put_object(Bucket=bucket_name, Key=s3_key, Body=file_data)

        logger.info(f"Uploaded files for {file_label} to S3 bucket {bucket_name}")

    except Exception as e:
        logger.error(f"Error uploading files from {file_path} to S3: {e}")
    
    finally:
        if os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)
        if os.path.exists(file_path):
            os.remove(file_path)

def lambda_handler(event, context):
    # Configuration of credentials and API URL
    api_key = os.environ.get('CDS_API_KEY')
    api_url = os.environ.get('CDS_API_URL')
    s3_bucket = os.environ.get('S3_BUCKET_NAME')

    # Initialization of the CDS API client
    c = cdsapi.Client(url=api_url, key=api_key)

    # Calculation of the previous month and current year
    today = datetime.date.today()
    previous_month = today.month - 1 or 12
    current_year = today.year if today.month > 1 else today.year - 1
    previous_month_str = f"{previous_month:02d}"
    days = [f"{day:02d}" for day in range(1, calendar.monthrange(current_year, previous_month)[1] + 1)]

    # List of variables to process and their corresponding file labels
    variables = {
        '2m_relative_humidity': 'Relative-Humidity',
        '10m_wind_speed': 'Wind-Speed',
        'solar_radiation_flux': 'Solar-Radiation-Flux',
        'precipitation_flux': 'Precipitation-Flux',
        '2m_temperature': 'Temperature-Air',
        '2m_dewpoint_temperature': 'DewPointTemperature',
    }

    results = []
    for variable, file_label in variables.items():
        result = download_and_upload_to_s3(c, variable, current_year, previous_month_str, days, s3_bucket, file_label)
        results.append(result)
        logger.info(f"Result for {variable}: {result['message']}")

    success_count = sum(1 for result in results if result['status'] == 'success')
    error_count = len(results) - success_count
    summary = f"Processing completed with {success_count} successes and {error_count} errors."
    logger.info(summary)
    return {"status": "complete", "summary": summary}
    