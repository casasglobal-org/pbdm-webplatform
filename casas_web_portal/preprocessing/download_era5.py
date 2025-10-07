import calendar
from datetime import date
import os
import tempfile
import logging
import zipfile
import cdsapi
import xarray as xr

from django.conf import settings

from casas_web_portal.functions import (
    days_range,
    merge_nc_files,
    rename_array,
    min_array,
    HUMI_TIMES,
    VARIABLES,
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ERA5_DIR = os.path.join(settings.DATA_DIR, "era5")
if not os.path.exists(ERA5_DIR):
    os.makedirs(ERA5_DIR)
DATASET = "sis-agrometeorological-indicators"


def _download_process_data(request, output_dir=ERA5_DIR):
    """
    Download and process data from the Copernicus Climate Data Store (CDS).

    Args:
        request: The request parameters for data retrieval.
        output_dir: The directory to save the downloaded and processed files.
    """
    try:
        # Copernicus URL and API Key
        url = os.environ.get("CDS_API_URL", "https://cds.climate.copernicus.eu/api")
        key = os.environ.get("CDS_API_KEY")
        if key is None:
            raise ValueError("CDS_API_KEY environment variable is not set.")
        # Initialize CDS API
        client = cdsapi.Client(url=url, key=key)

        # temporary directory for downloads and extraction
        label = request.get("variable", "data").replace(" ", "_")
        year = request.get("year")
        month_str = request.get("month")
        if "statistic" in request.keys():
            statistic = request.get("statistic", "").replace(" ", "_")
        elif "time" in request.keys():
            statistic = request.get("time", "").replace(":", "_")
        else:
            statistic = None
        if statistic:
            extract_to = os.path.join(output_dir, f"{label}_{statistic}")
        else:
            extract_to = os.path.join(output_dir, label)
        extract_to = extract_to.rstrip("").rstrip("_")
        os.makedirs(extract_to, exist_ok=True)
        zip_file = f"{extract_to}/{year}-{month_str}.zip"

        # Download the zip data
        print(f"Requesting data with parameters: {request}")
        logger.info("Downloading data from CDS...")
        result = client.retrieve(DATASET, request)
        result.download(target=zip_file)
        logger.info("Download completed.")

        # Extract the zip file
        logger.info("Extracting files...")
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(extract_to)
        logger.info("Extraction completed.")

        # Merge NetCDF files using xarray
        merge_nc_files(
            extract_to,
            f"{label}-{year}-{month_str}-merged.nc",
            f"*{year}{month_str}*.nc",
        )

        logger.info("Merge completed.")
        return True
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise Exception(f"Data processing failed: {e}")


def _all_data_download(
    element,
    start_date=None,
    end_date=None,
    output_dir=ERA5_DIR,
    merge_year=True,
):
    """Process all data from the Copernicus Climate Data Store (CDS).

    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): Directory to save the downloaded files. Defaults to ERA5_DIR.
    """
    dates = days_range(start_date, end_date)
    label = VARIABLES[element]["era5"]
    stat = VARIABLES[element]["era5_stat"]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    # for each year and month in the range
    for year, months in dates.items():
        for month, days in months.items():
            month_str = str(month).zfill(2)
            request = {
                "format": "zip",
                "variable": label,
                "year": str(year),
                "month": month_str,
                "day": days,
                "version": "2_0",
            }
            if stat:
                request["statistic"] = stat
            _download_process_data(request, output_dir)
        if merge_year:
            # Merge NetCDF files using xarray
            if stat:
                extract_to = os.path.join(output_dir, f"{label}_{stat}")
            else:
                extract_to = os.path.join(output_dir, label)
            merge_nc_files(
                extract_to,
                f"{label}-{year}-merged.nc",
                f"{label}*{year}-*-merged.nc",
                remove=False,
            )


def download_wind(start_date=None, end_date=None, output_dir=ERA5_DIR, merge_year=True):
    """
    Process wind data from the Copernicus Climate Data Store (CDS).

    Args:
        start_date: The start date for the data retrieval.
        end_date: The end date for the data retrieval.
        output_dir: Directory to save the downloaded files.
        merge_year: If True, merge monthly data into yearly files. Defaults to True.

    """
    _all_data_download("wind", start_date, end_date, output_dir, merge_year)


def download_solar_radiation(
    start_date=None, end_date=None, output_dir=ERA5_DIR, merge_year=True
):
    """Process solar radiation data from the Copernicus Climate Data Store (CDS).

    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): Directory to save the downloaded files. Defaults to ERA5_DIR.
        merge_year (bool, optional): If True, merge monthly data into yearly files. Defaults to True.
    """
    _all_data_download("solar", start_date, end_date, output_dir, merge_year)


def download_precipitation(
    start_date=None, end_date=None, output_dir=ERA5_DIR, merge_year=True
):
    """
    Process precipitation data from the Copernicus Climate Data Store (CDS).

    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): Directory to save the downloaded files. Defaults to ERA5_DIR.
        merge_year (bool, optional): If True, merge monthly data into yearly files. Defaults to True.
    """
    _all_data_download("prec", start_date, end_date, output_dir, merge_year)


def download_temperature(
    start_date=None, end_date=None, output_dir=ERA5_DIR, merge_year=True
):
    """
    Process temperature data from the Copernicus Climate Data Store (CDS).
    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): Directory to save the downloaded files. Defaults to ERA5_DIR.
        merge_year (bool, optional): If True, merge monthly data into yearly files. Defaults to True.
    """
    _all_data_download("tmax", start_date, end_date, output_dir, merge_year)
    _all_data_download("tmin", start_date, end_date, output_dir, merge_year)


def download_humidity(
    start_date=None,
    end_date=None,
    output_dir=ERA5_DIR,
    merge_year=True,
    min_value=True,
):
    """Process humidity data from the Copernicus Climate Data Store (CDS).

    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): Directory to save the downloaded files. Defaults to ERA5_DIR.
        merge_year (bool, optional): If True, merge monthly data into yearly files. Defaults to True.
        min_value (bool, optional): If True, calculate minimum daily humidity. Defaults to True.
    """
    # Calculate the previous month and year
    dates = days_range(start_date, end_date)
    label = "2m_relative_humidity"
    if not os.path.exists(os.path.join(output_dir, f"{label}_min")):
        os.makedirs(os.path.join(output_dir, f"{label}_min"), exist_ok=True)
    for year, months in dates.items():
        for month, days in months.items():
            files = []
            for time in HUMI_TIMES:
                month_str = str(month).zfill(2)
                request = {
                    "version": "2_0",
                    "format": "zip",
                    "variable": label,
                    "year": str(year),
                    "month": month_str,
                    "day": days,
                    "time": time,
                }
                _download_process_data(request, output_dir)
                file = os.path.join(
                    output_dir,
                    f"{label}_{time}",
                    f"{label}-{year}-{month_str}-merged.nc",
                )
                rm_file = os.path.join(
                    output_dir,
                    f"{label}_{time}",
                    f"{label}-{year}-{month_str}-merged-toremove.nc",
                )
                os.rename(file, rm_file)

                files.append(file)
                new_array = rename_array(
                    xr.open_dataset(rm_file),
                    {
                        f"Relative_Humidity_2m_{time.split('_')[0]}h": VARIABLES[
                            "rel_humidity"
                        ]["era5_variable"]
                    },
                )
                new_array.to_netcdf(file)
                new_array.close()
                os.remove(rm_file)
            print(f"Calculating minimum daily humidity for {year}-{month_str}")
            array_min = min_array(
                files,
                None,
                date(year, month, 1),
                date(year, month, int(days[-1])),
            )
            array_min.to_netcdf(
                os.path.join(
                    output_dir,
                    f"{label}_min",
                    f"{label}-{year}-{month_str}-merged.nc",
                )
            )

        if merge_year:
            # Merge NetCDF files using xarray
            extract_to = os.path.join(output_dir, f"{label}_min")
            merge_nc_files(
                extract_to,
                f"{label}-{year}-merged.nc",
                f"{label}*{year}-*-merged.nc",
                remove=False,
            )
            for time in HUMI_TIMES:
                extract_to = os.path.join(output_dir, f"{label}_{time}")
                merge_nc_files(
                    extract_to,
                    f"{label}-{year}-merged.nc",
                    f"{label}*{year}-*-merged.nc",
                    remove=False,
                )
    return True


def download_all(start_date=None, end_date=None, output_dir=ERA5_DIR):
    """Process all data from the Copernicus Climate Data Store (CDS).

    Args:
        start_date (str, optional): The start date for the data retrieval. Defaults to None.
        end_date (str, optional): The end date for the data retrieval. Defaults to None.
        output_dir (str, optional): Directory to save the downloaded files. Defaults to ERA5_DIR.
    """
    download_precipitation(start_date, end_date, output_dir)
    download_temperature(start_date, end_date, output_dir)
    download_wind(start_date, end_date, output_dir)
    download_solar_radiation(start_date, end_date, output_dir)
    download_humidity(start_date, end_date, output_dir)
