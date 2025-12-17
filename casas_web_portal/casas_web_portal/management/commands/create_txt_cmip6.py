import logging
import os
from django.core.management.base import BaseCommand, CommandError
from casas_web_portal.functions import (
    calculate_all_casas_txt_month,
    calculate_all_casas_txt,
)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Command(BaseCommand):
    """_summary_"""

    help = "Create txt file ERA5 data for one year"

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)
        parser.add_argument(
            "--dir",
            type=str,
            help="Directory containing 'data' and 'txt' folders",
        )
        parser.add_argument(
            "--base",
            type=str,
            help="Base name for output txt files. Default: casas_cmip6",
            default="casas_cmip6",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit number of locations to process (for testing)",
            default=None,
        )
        parser.add_argument(
            "--monthly",
            action="store_true",
            help="Process data monthly instead of yearly",
        )

    def handle(self, *args, **options):
        year = options["year"]
        directory = options["dir"]
        data_dir = os.path.join(directory, "data", "cmip6")
        txt_dir = os.path.join(directory, "txt", "cmip6")
        if not os.path.exists(txt_dir):
            os.makedirs(txt_dir)
        if not year:
            self.print_help()
        logger.info(f"Create txt CMIP6 data for {year}")
        if options["monthly"]:
            calculate_all_casas_txt_month(
                year,
                data_dir,
                txt_dir,
                provider="cmip6",
                outbase=options["base"],
                limit=options["limit"],
            )
        else:
            calculate_all_casas_txt(
                year, data_dir, txt_dir, provider="cmip6", outbase=options["base"]
            )
