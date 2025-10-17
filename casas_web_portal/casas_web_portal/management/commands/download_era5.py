import logging
from django.core.management.base import BaseCommand, CommandError
from preprocessing.download_era5 import download_all


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    """_summary_"""

    help = "download ERA5 data for one year"

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)

    def handle(self, *args, **options):
        year = options["year"]
        if not year:
            self.print_help()
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        logger.info(f"Download ERA5 data for {year}")
        download_all(start_date, end_date)
