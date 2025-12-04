import os
import logging
import requests
import tempfile
from django.conf import settings
from casas_web_portal.functions import start_end_dates, merge_nc_files, VARIABLES

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

BASE_URL = "https://ds.nccs.nasa.gov/thredds/fileServer/AMES/NEX/GDDP-CMIP6"

MODELS = [("MPI-ESM1-2-HR", "historical"), ("MPI-ESM1-2-HR", "ssp585")]

CMIP6_DIR = os.path.join(settings.DATA_DIR, "cmip6")
if not os.path.exists(CMIP6_DIR):
    os.makedirs(CMIP6_DIR)


def _download_process_data(url, filename):
    """
    Download and process data from the given URL.

    Args:
        url: The URL to download the data from.
        filename: The local filename to save the downloaded data.

    Returns:
        bool: True if download and processing were successful, False otherwise.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        with open(filename, "wb") as file:
            file.write(response.content)
        logger.info(f"Downloaded file: {filename}")
        return True
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False


def _all_data_download(
    variable,
    start_date=None,
    end_date=None,
    output_dir=CMIP6_DIR,
    version="v2.0",
):
    """Process temperature data from NASA GDDP-CMIP6 dataset.

    Args:
        variable (str): The variable name to download.
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): The directory to save the output files. Defaults to settings.DATA_DIR joined "cmip6".
        version (str, optional): The version of the dataset to download. Defaults to "v2.0".
    Returns:
        bool: True if processing was successful, False otherwise.
    """
    dates = start_end_dates(start_date, end_date)
    years = range(dates[0].year, dates[1].year + 1)
    extract_to = os.path.join(output_dir, variable)
    os.makedirs(extract_to, exist_ok=True)
    for model in MODELS:
        key = model[0]
        val = model[1]
        for year in years:
            if version:
                filename = f"{variable}_day_{key}_{val}_r1i1p1f1_gn_{year}_{version}.nc"
            else:
                filename = f"{variable}_day_{key}_{val}_r1i1p1f1_gn_{year}.nc"
            file = os.path.join(extract_to, filename)
            url = f"{BASE_URL}/{key}/{val}/r1i1p1f1/{variable}/{filename}"  # ?var=pr&north={coords[3]}&west={coords[0]}&east={coords[2]}&south={coords[1]}&horizStride=1&time_start={dates[0].strftime("%Y-%m-%d")}&time_end={dates[1].strftime("%Y-%m-%d")}&timeStride=&vertCoord=&accept={format}&addLatLon=true"
            _download_process_data(url, file)
    return True


def download_temperature(
    start_date=None,
    end_date=None,
    output_dir=CMIP6_DIR,
    version="v2.0",
):
    """Download and process temperature data from NASA GDDP-CMIP6 dataset.

    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): The directory to save the output files. Defaults to settings.DATA_DIR joined "cmip6".
        version (str, optional): The version of the dataset to download. Defaults to "v2.0".

    """
    _all_data_download(
        VARIABLES["tmin"]["cmip6"], start_date, end_date, output_dir, version
    )
    _all_data_download(
        VARIABLES["tmax"]["cmip6"], start_date, end_date, output_dir, version
    )


def download_humidity(
    start_date=None,
    end_date=None,
    output_dir=CMIP6_DIR,
    version="v2.0",
):
    """Download and process humidity data from NASA GDDP-CMIP6 dataset.

    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): The directory to save the output files. Defaults to settings.DATA_DIR joined "cmip6".
        version (str, optional): The version of the dataset to download. Defaults to "v2.0".
    """
    _all_data_download(
        VARIABLES["rel_humidity"]["cmip6"], start_date, end_date, output_dir, version
    )


def download_precipitation(
    start_date=None,
    end_date=None,
    output_dir=CMIP6_DIR,
    version="v2.0",
):
    """Download and process precipitation data from NASA GDDP-CMIP6 dataset.

    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): The directory to save the output files. Defaults to settings.DATA_DIR joined "cmip6".
        version (str, optional): The version of the dataset to download. Defaults to "v2.0".
    """
    _all_data_download(
        VARIABLES["prec"]["cmip6"], start_date, end_date, output_dir, version
    )


def download_wind(
    start_date=None,
    end_date=None,
    output_dir=CMIP6_DIR,
    version="v2.0",
):
    """Download and process wind data from NASA GDDP-CMIP6 dataset.

    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): The directory to save the output files. Defaults to settings.DATA_DIR joined "cmip6".
        version (str, optional): The version of the dataset to download. Defaults to "v2.0".
    """
    _all_data_download(
        VARIABLES["wind"]["cmip6"], start_date, end_date, output_dir, version
    )


def download_solar(
    start_date=None,
    end_date=None,
    output_dir=CMIP6_DIR,
    version="v2.0",
):
    """Download and process solar radiation data from NASA GDDP-CMIP6 dataset.

    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): The directory to save the output files. Defaults to settings.DATA_DIR joined "cmip6".
        version (str, optional): The version of the dataset to download. Defaults to "v2.0".
    """
    _all_data_download(
        VARIABLES["solar"]["cmip6"], start_date, end_date, output_dir, version
    )


def download_all(start_date=None, end_date=None, output_dir=CMIP6_DIR, version="v2.0"):
    """Download and process all variables from NASA GDDP-CMIP6 dataset.
    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): The directory to save the output files. Defaults to settings.DATA_DIR joined "cmip6".
        version (str, optional): The version of the dataset to download. Defaults to "v2.0".
    """
    download_precipitation(start_date, end_date, output_dir, version)
    download_humidity(start_date, end_date, output_dir, version)
    download_temperature(start_date, end_date, output_dir, version)
    download_wind(start_date, end_date, output_dir, version)
    download_solar(start_date, end_date, output_dir, version)
