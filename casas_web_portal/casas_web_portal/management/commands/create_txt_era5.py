import logging
import os
from django.core.management.base import BaseCommand, CommandError
from casas_web_portal.functions import calculate_all_casas_txt_month


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    """_summary_"""

    help = "Create txt file ERA5 data for one year"

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)
        parser.add_argument(
            "--dir",
            "dir",
            type=str,
            help="Directory containing 'data' and 'txt' folders",
        )
        parser.add_argument(
            "--base",
            "base",
            type=str,
            help="Base name for output txt files",
            default="casas_era5_",
        )

    def handle(self, *args, **options):
        year = options["year"]
        directory = options["dir"]
        data_dir = os.path.join(directory, "data", "era5")
        txt_dir = os.path.join(directory, "txt", "era5")
        if not os.path.exists(txt_dir):
            os.makedirs(txt_dir)
        if not year:
            self.print_help()
        logger.info(f"Create txt ERA5 data for {year}")
        calculate_all_casas_txt_month(year, data_dir, txt_dir, outbase=options["base"])
