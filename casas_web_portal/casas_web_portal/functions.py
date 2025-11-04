import os
import logging
import calendar
from datetime import date, datetime, timedelta
import glob
import gzip
import rioxarray
import xarray as xr
import fiona
from casas_web_portal import settings
from django.core.mail import send_mail
from smtplib import SMTPException

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

VARIABLES = {
    "rel_humidity": {
        "era5": "2m_relative_humidity",
        "era5_variable": "Relative_Humidity_2m",
        "era5_stat": "",
        "cmip6": "hurs",
        "cmip6_variable": "",
    },
    "tmin": {
        "era5": "2m_temperature",
        "era5_variable": "Temperature_Air_2m_Min_24h",
        "era5_stat": "24_hour_minimum",
        "cmip6": "tasmin",
        "cmip6_variable": "",
    },
    "tmax": {
        "era5": "2m_temperature",
        "era5_variable": "Temperature_Air_2m_Max_24h",
        "era5_stat": "24_hour_maximum",
        "cmip6": "tasmax",
        "cmip6_variable": "",
    },
    "prec": {
        "era5": "precipitation_flux",
        "era5_variable": "Precipitation_Flux",
        "era5_stat": None,
        "cmip6": "pr",
        "cmip6_variable": "",
    },
    "solar": {
        "era5": "solar_radiation_flux",
        "era5_variable": "Solar_Radiation_Flux",
        "era5_stat": None,
        "cmip6": "rsds",
        "cmip6_variable": "",
    },
    "wind": {
        "era5": "10m_wind_speed",
        "era5_variable": "Wind_Speed_10m_Mean_24h",
        "era5_stat": "24_hour_mean",
        "cmip6": "sfcWind",
        "cmip6_variable": "",
    },
}

HUMI_TIMES = ["06_00", "09_00", "12_00", "15_00", "18_00"]


def _send_mail(title, text, user):
    """Send an email to the user.

    Args:
        title (str): The subject of the email.
        text (str): The body of the email.
        user (User): The user to send the email to.

    Raises:
        ValueError: If there is an error sending the email.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    try:
        sent = send_mail(
            title,
            text,
            settings.EMAIL_HOST_USER,
            [user.email, settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
    except SMTPException as err:
        logger.error(f"Error sending email to user {user.username}: {err}")
        raise ValueError(f"Error sending email to user {user.username}: {err}")
    if sent == 0:
        logger.error(f"Error sending email to user {user.username}")
        raise ValueError(f"Error sending email to user {user.username}")
    return True


def start_end_dates(start_date=None, end_date=None, delta_days=30):
    """Return the start and end dates as datetime objects.

    Args:
        start_date (optional): The starting date, it should be the oldest one. Defaults to None.
        end_date (optional): The ending date, it should be the most recent one. Defaults to None.
        delta_days (int, optional): The number of days to look back from today. Defaults to 30.

    Raises:
        ValueError: If start_date is not a string or datetime.
        ValueError: If end_date is not a string or datetime.
        ValueError: If start_date is after end_date.

    Returns:
        tuple: A tuple containing the start and end dates as datetime objects.
    """

    date_format = "%Y-%m-%d"
    if not start_date:
        start = datetime.now() - timedelta(days=delta_days)
    elif isinstance(start_date, str):
        start = datetime.strptime(start_date, date_format)
    elif isinstance(start_date, datetime) or isinstance(start_date, date):
        start = start_date
    else:
        raise ValueError(
            "start_date must be a string in 'YYYY-MM-DD' format or a datetime object."
        )

    if not end_date:
        end = datetime.now()
    elif isinstance(end_date, str):
        end = datetime.strptime(end_date, date_format)
    elif isinstance(end_date, datetime) or isinstance(end_date, date):
        end = end_date
    else:
        raise ValueError(
            "end_date must be a string in 'YYYY-MM-DD' format or a datetime object."
        )

    if start > end:
        raise ValueError("Start date must be before end date.")

    return start, end


def days_range(start_date, end_date):
    """Generate a list of date strings between start_date and end_date.

    Args:
        start_date (str or datetime): The starting date.
        end_date (str or datetime): The ending date.

    Returns:
        list: A list of date strings in 'YYYY-MM-DD' format.
    """
    start, end = start_end_dates(start_date, end_date)
    delta = end - start
    output = {}
    for i in range(delta.days + 1):
        newdata = start + timedelta(days=i)
        if newdata.year not in output:
            output[newdata.year] = {}
        if newdata.month not in output[newdata.year]:
            output[newdata.year][newdata.month] = []
        output[newdata.year][newdata.month].append(newdata.strftime("%d"))
    return output


def split_list(a, n):
    """Function to split list in n even parts

    Args:
        a (list): the list to split
        n (int): the number of parts
    Returns:
        list: a list of n lists
    """
    k, m = divmod(len(a), n)
    return list((a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n)))


def merge_nc_files(extract_to, output_filename, pattern, remove=True):
    """Merge multiple .nc files in a directory into a single .nc file using xarray.

    Args:
        extract_to (str): Directory containing the .nc files to merge.
        output_filename (str): Name of the resulting merged .nc file.
        pattern (str): String to filter correctly the NetCDF files to merge
        remove (bool, optional): Whether to remove the original files after merging. Defaults to True.

    Returns:
        Path to the merged .nc file.
    """
    output_file_path = os.path.join(extract_to, output_filename)
    nc_files = sorted(
        [os.path.join(extract_to, f) for f in glob.glob1(extract_to, pattern)]
    )
    logger.debug(f"Found {len(nc_files)} .nc files to merge in {extract_to}")
    logger.debug(f"Files: {nc_files}")

    if not nc_files:
        logger.info(
            f"No .nc files found to merge in the directory {extract_to} with pattern {pattern}"
        )
        return None

    datasets = []

    try:
        datasets = [xr.open_dataset(nc_file) for nc_file in nc_files]
        combined_ds = xr.concat(datasets, dim="time")
        combined_ds.to_netcdf(output_file_path)
        logger.info(f"Files merged successfully into {output_file_path}")
    except Exception as e:
        logger.error(f"Failed to merge .nc files with xarray: {e}")
        raise
    finally:
        for ds in datasets:
            ds.close()
        if remove:
            for nc_file in nc_files:
                os.remove(nc_file)

    return output_file_path


def mean_array(paths, geom, start, end, crs="EPSG:4326", grid=False):
    """Function to calculate mean value for a variable from a list of NetCDF files

    Args:
        paths (list): the list of paths to the NetCDF files
        geom (list): a list of dictionary with GeoJSON format polygon
                     [{'type': 'Polygon', 'coordinates': [[[10, 45], [11, 46], [12, 45], [10, 45]]]}]
        start (obj, str): the starting date
        end (obj, str): the ending date
        crs (str, optional): the CRS used, default EPSG=4326.
        grid (bool, optional): Whether to stack longitude and latitude dimensions
                               in a new column called grid. Defaults to False.

    Returns:
        xarray.Dataset: the mean xarray dataset
    """

    ncs = []
    for path in paths:
        ncs.append(read_nc(path, geom, start, end, crs, grid))
    mean_dataset = ncs[0].copy(deep=True)
    for var in ncs[0].data_vars:
        stacked = xr.concat([ds[var] for ds in ncs], dim="dataset")
        mean_dataset[var] = stacked.mean(dim="dataset")
    return mean_dataset


def min_array(paths, geom, start, end, crs="EPSG:4326", grid=False):
    """Function to calculate mean value for a variable from a list of NetCDF files

    Args:
        paths (list): the list of paths to the NetCDF files
        geom (list): a list of dictionary with GeoJSON format polygon
                     [{'type': 'Polygon', 'coordinates': [[[10, 45], [11, 46], [12, 45], [10, 45]]]}]
        start (obj, str): the starting date
        end (obj, str): the ending date
        crs (str, optional): the CRS used, default EPSG=4326.
        grid (bool, optional): Whether to stack longitude and latitude dimensions
                               in a new column called grid. Defaults to False.

    Returns:
        xarray.Dataset: the minimum xarray dataset
    """

    ncs = []
    for path in paths:
        ncs.append(read_nc(path, geom, start, end, crs, grid))
    min_dataset = ncs[0].copy(deep=True)
    stacked = xr.concat(ncs, dim="ensemble")  # o nome qualsiasi
    ds_min = stacked.min(dim="ensemble", skipna=True)
    for var in ncs[0].data_vars:
        min_dataset[var] = ds_min[var]
    min_dataset.rio.write_crs(crs, inplace=True)
    return min_dataset


def rename_array(array, new_names):
    """Function to rename the variables in a xarray object

    Args:
        array (xarray.Dataset): the xarray object
        new_names (dict): the dictionary with the new names

    Returns:
        xarray.Dataset: the renamed xarray object
    """
    return array.rename(new_names)


def read_nc(path, geom, start, end, crs="EPSG:4326", grid=True):
    """Function to read the NetCDF file and filter for geometry
       and start and end date

    Args:
        path (str): The path to the NetCDF file
        geom (dict): a list of dictionary with GeoJSON format polygon
                     [{'type': 'Polygon', 'coordinates': [[[10, 45], [11, 46], [12, 45], [10, 45]]]}]
        start (obj): Date object for the starting date
        end (obj): Date object for the ending date
        crs (str): the CRS used, default EPSG=4326
        grid (bool, optional): Whether to stack longitude and latitude dimensions
                               in a new column called grid. Defaults to True.


    Returns:
        A xarray object filtered
    """
    xds = xr.open_dataset(path)
    if {"lat", "lon"}.issubset(xds.dims):
        xds = xds.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    elif {"x", "y"}.issubset(xds.dims):
        pass  # già OK
    else:
        raise ValueError("Dataset missing required spatial dimensions.")

    if not xds.rio.crs:
        xds = xds.rio.write_crs(crs)
    xds.rio.write_coordinate_system(inplace=True)
    selected = xds.sel(time=slice(start, end))
    xds.close()
    if geom:
        final = selected.rio.clip(geom, crs)
    else:
        final = selected
    if grid:
        return final.stack(grid=["lat", "lon"])
    return final


def write_casas_files(outdir, data, basename="mpi_esm_lr_", country=None):
    """Function to write the txt file

    Args:
        outdir (str): the output directory
        data (dict): the data dictionary
        basename (str, optional): the base name of the output txt files. Defaults to "mpi_esm_lr_".

    Returns:
        str: the path to the output txt file
    """
    if country:
        outname = (
            f"{basename}_{data['rowcol']['x']}_{data['rowcol']['y']}_{country}.txt.gz"
        )
    else:
        outname = f"{basename}_{data['rowcol']['x']}_{data['rowcol']['y']}.txt.gz"
    outfile = os.path.join(outdir, outname)
    if not os.path.exists(outfile):
        with gzip.open(outfile, "wt") as f:
            f.write(f"{outfile}\n")
            f.write(f"{data['coords']['x']}\t{data['coords']['y']}\n")
            f.write("MO\tDA\tYEAR\tTMAX\tTMIN\tSOL\tPRCP\tRH\tWIND\n")

    with gzip.open(outfile, "at") as f:
        for i, mydate in enumerate(data["dates"]):
            split_date = str(mydate.astype("datetime64[D]")).split("-")
            line = (
                f"{split_date[1]}\t{split_date[2]}\t{split_date[0]}\t"
                f"{data['tmax'][i]:.1f}\t{data['tmin'][i]:.1f}\t"
                f"{data['solar'][i]:.1f}\t{data['precip'][i]:.1f}"
                f"\t{data['rh'][i]:.1f}\t{data['wind'][i]:.1f}\n"
            )
            f.write(line)
    return outfile


def write_casas_txt(
    list_coords, start, end, indir, outdir, provider="era5", outbase="mpi_esm_lr_"
):
    """Function to read NC files and write the txt file to be passed

    Args:
        list_coords (list): a list of tuples with the coordinates [(lon, lat), (lon, lat),]
        start (obj): a string in 'YYYY-MM-DD' format or a date object
                     representing the start date
        end (obj): a string in 'YYYY-MM-DD' format or a date object
                   representing the final date
        indir (str): a string of the directory with input data
        outdir (str): a string of the directory where to write the output data
        provider (str, optional): The provider of data. Defaults to "era5",
                                  other accepted value is "cmip6".
        outbase (str, optional): _description_. Defaults to "mpi_esm_lr_".
    """
    start_date, end_date = start_end_dates(start, end)
    outfiles = []
    prov_var = f"{provider}_variable"
    geom = None
    for year in range(start_date.year, end_date.year + 1):
        if year == start_date.year:
            start_month = start_date.month
        else:
            start_month = 1
        if year == end_date.year:
            end_month = end_date.month
        else:
            end_month = 12
        res = calendar.monthrange(year, end_month)
        last_day = res[1]
        this_start = date(year, start_month, 1)
        this_end = date(year, end_month, last_day)
        print(f"Processing year {year} from {this_start} to {this_end}")

        tmin_file = os.path.join(
            indir,
            f'{VARIABLES["tmin"][provider]}_24_hour_minimum',
            f'{VARIABLES["tmin"][provider]}-{year}-merged.nc',
        )
        tmin_nc = read_nc(tmin_file, geom, this_start, this_end, grid=False)
        print(f"Got tmin data")
        if provider == "era5":
            # conversion from K to C
            tmin_nc = tmin_nc - 273.15
        tmax_file = os.path.join(
            indir,
            f'{VARIABLES["tmax"][provider]}_24_hour_maximum',
            f'{VARIABLES["tmax"][provider]}-{year}-merged.nc',
        )
        tmax_nc = read_nc(tmax_file, geom, this_start, this_end, grid=False)
        print(f"Got tmax data")
        if provider == "era5":
            # conversion from K to C
            tmax_nc = tmax_nc - 273.15
        prec_file = os.path.join(
            indir,
            f'{VARIABLES["prec"][provider]}',
            f'{VARIABLES["prec"][provider]}-{year}-merged.nc',
        )
        prec_nc = read_nc(prec_file, geom, this_start, this_end, grid=False)
        print(f"Got precip data")
        solar_file = os.path.join(
            indir,
            f'{VARIABLES["solar"][provider]}',
            f'{VARIABLES["solar"][provider]}-{year}-merged.nc',
        )
        solar_nc = read_nc(solar_file, geom, this_start, this_end, grid=False)
        if provider == "era5":
            # conversion from J m^-2 day^-1 to W m^-2
            solar_nc = solar_nc / 86400
        print(f"Got solar data")
        wind_file = os.path.join(
            indir,
            f'{VARIABLES["wind"][provider]}_24_hour_mean',
            f'{VARIABLES["wind"][provider]}-{year}-merged.nc',
        )
        wind_nc = read_nc(wind_file, geom, this_start, this_end, grid=False)
        print(f"Got wind data")
        humi_file = os.path.join(
            indir,
            f'{VARIABLES["rel_humidity"][provider]}_min',
            # f'{VARIABLES["rel_humidity"][provider]}_06_00',
            f'{VARIABLES["rel_humidity"][provider]}-{year}-merged.nc',
        )
        humi_nc = read_nc(humi_file, geom, this_start, this_end, grid=False)
        print(f"Got all data for year {year}, writing files")

        for coord in list_coords:
            lon, lat = coord["geom"]
            coords = xr.Dataset(coords={"lon": lon, "lat": lat})
            data = {
                "coords": {"x": coords.lon.values, "y": coords.lat.values},
                "rowcol": {"x": coord["rowcol"][0], "y": coord["rowcol"][1]},
            }
            vals = prec_nc[VARIABLES["prec"][prov_var]].sel(
                lon=lon, lat=lat, method="nearest"
            )
            data["dates"] = vals.time.values
            data["precip"] = vals.values
            vals = tmax_nc[VARIABLES["tmax"][prov_var]].sel(
                lon=lon, lat=lat, method="nearest"
            )
            data["tmax"] = vals.values
            vals = tmin_nc[VARIABLES["tmin"][prov_var]].sel(
                lon=lon, lat=lat, method="nearest"
            )
            data["tmin"] = vals.values
            vals = solar_nc[VARIABLES["solar"][prov_var]].sel(
                lon=lon, lat=lat, method="nearest"
            )
            data["solar"] = vals.values
            vals = wind_nc[VARIABLES["wind"][prov_var]].sel(
                lon=lon, lat=lat, method="nearest"
            )
            data["wind"] = vals.values
            vals = humi_nc[VARIABLES["rel_humidity"][prov_var]].sel(
                lon=lon, lat=lat, method="nearest"
            )
            data["rh"] = vals.values
            outfile = write_casas_files(outdir, data, outbase)
            if outfile not in outfiles:
                outfiles.append(outfile)
    return outfiles


def _read_file_for_coords(file_path, limit=None):
    """Helper function to read a single file for specific coordinates.

    Args:
        file_path (str): Path to the data file.
        limit (int, optional): Limit number of locations to process. Defaults to None.
    Returns:
        dict: Data list for the given coordinates.
    """
    list_coords = []
    with fiona.open(file_path) as src:
        if limit:
            features = list(src)[:limit]
        else:
            features = list(src)
        for feature in features:
            geom = feature["geometry"]
            coords = geom["coordinates"]
            list_coords.append(
                {
                    "geom": tuple(coords),
                    "rowcol": tuple(
                        [feature["properties"]["x"], feature["properties"]["y"]]
                    ),
                }
            )
    return list_coords


def calculate_all_casas_txt_month(
    year, indir, outdir, provider="era5", outbase="mpi_esm_lr_", limit=None
):
    """"""
    filepath = os.path.join(
        settings.STATIC_ROOT, "data", "{}_grid_land.fgb".format(provider)
    )
    list_coords = _read_file_for_coords(filepath, limit=limit)
    for month in range(1, 13):
        print(f"Processing month {month} of year {year}")
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year, 12, 31)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        outfiles = write_casas_txt(
            list_coords, start_date, end_date, indir, outdir, provider, outbase
        )
    return outfiles


def calculate_all_casas_txt(
    year, indir, outdir, provider="era5", outbase="mpi_esm_lr_", limit=None
):
    """"""
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    list_coords = _read_file_for_coords(
        os.path.join(settings.STATIC_ROOT, "data", "{}_grid_land.fgb".format(provider)),
        limit=limit,
    )
    outfiles = write_casas_txt(
        list_coords, start_date, end_date, indir, outdir, provider, outbase
    )
    return outfiles
