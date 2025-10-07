import logging
from django.core.management.base import BaseCommand, CommandError
from preprocessing.download_era5 import download_all


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    """_summary_"""

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)

    def handle(self, *args, **options):
        start_date = f"{options['year']}-01-01"
        end_date = f"{options['year']}-12-31"
        logger.info(f"Download ERA5 data for {options['year']}")
        download_all(start_date, end_date)
