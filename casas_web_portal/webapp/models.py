import gzip
import os
import tempfile
import zipfile

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
from django.core.files import File
from django.utils import timezone
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

# Create your models here.

GRID_DIR = os.path.join(settings.BASE_DIR, "webapp", "static", "data")
SCRIPTS_DIR = os.path.join(settings.BASE_DIR, "scripts")
GIS_OUTPUT_INTERVAL = 30

CONTINENT = (
    ("EU", _("Europe")),
    ("AS", _("Asia")),
    ("AF", _("Africa")),
    ("NA", _("North America")),
    ("SA", _("South America")),
    ("OC", _("Oceania")),
)

PDBMS = (("olive", _("Olive")), ("another", _("Another")))

WEATHERS = (("era5", "AgERA5 v2.0"), ("cmip6", "NEX-GDDP-CMIP6 v2.0"))


class BaseDigi(models.Model):
    """Class for base model for simple"""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ["name"]
        abstract = True

    def __str__(self):
        return smart_str(self.name)

    def natural_key(self):
        return self.__str__()

    def __lt__(self, other):
        return self.__str__() < other.__str__()

    def __gt__(self, other):
        return self.__str__() > other.__str__()


class Country(BaseDigi):
    """Class for country info"""

    shortname = models.CharField(max_length=3)
    geom = models.MultiPolygonField(srid=4326, geography=True)
    continent = models.CharField(max_length=2, choices=CONTINENT, null=True, blank=True)

    class Meta(BaseDigi.Meta):
        db_table = "general_country"


class Organization(BaseDigi):
    """This table is useful to save info about organizations"""

    # TODO maybe extent group class with this?
    shortname = models.CharField(max_length=15)
    address = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, null=True, blank=True
    )
    email = models.EmailField(null=True, blank=True)
    website = models.CharField(max_length=150, null=True, blank=True)
    image = models.ImageField(
        upload_to="organizations/",
        null=True,
        blank=True,
        help_text=_("The organization logo"),
    )
    geom = models.PointField(
        srid=4326,
        geography=True,
        null=True,
        blank=True,
        help_text=_("The position of the organization"),
    )

    class Meta(BaseDigi.Meta):
        db_table = "general_organization"

    def __str__(self):
        if self.country:
            return smart_str(
                "{na} ({co})".format(na=self.name, co=self.country.shortname)
            )
        else:
            return smart_str("{na}".format(na=self.name))


class User(AbstractUser):
    """Extent the abstract user class"""

    email = models.EmailField(_("email address"), unique=True)
    bio = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        help_text=_("Short user biography"),
    )
    image = models.ImageField(
        upload_to="users/", null=True, blank=True, help_text=_("User image")
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, null=True, blank=True
    )

    class Meta:
        db_table = "general_user"

    @property
    def full_name(self):
        return self.get_full_name()


class Job(BaseDigi):
    """Class for job info"""

    description = models.TextField(
        null=True, blank=True, help_text=_("A short description of the job")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        help_text=_("The user that created the job"),
    )
    start_date = models.DateField()
    end_date = models.DateField()
    model = models.CharField(choices=PDBMS, help_text=_("The chosen PDMB model"))
    weather = models.CharField(choices=WEATHERS, help_text=_("The chosen weather data"))
    geom = models.MultiPolygonField(
        srid=4326,
        geography=True,
        help_text=_("The area of interest for the job"),
    )
    image = models.ImageField(
        upload_to="jobs/",
        null=True,
        blank=True,
        help_text=_("A screenshot image of the job"),
    )
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True, blank=True)
    ended = models.DateTimeField(null=True, blank=True)
    is_public = models.BooleanField(
        default=False,
        help_text=_("If true the job is visible to all the users"),
    )
    model_output = models.FileField(
        upload_to="model_output/",
        null=True,
        blank=True,
        help_text=_("The output file of the job"),
    )

    gis_output = models.FileField(
        upload_to="gis_output/",
        null=True,
        blank=True,
        help_text=_("The output file of the job"),
    )

    class Meta(BaseDigi.Meta):
        db_table = "general_job"
        ordering = ["-created"]

    def __str__(self):
        output = f"{self.name} {self.model} {self.weather} - {self.start_date}/{self.end_date}"
        return smart_str(output)

    def run_model(self):
        """Run the PDMB model on every grid cell intersecting the job area.

        The model is executed in a dedicated working directory for each cell
        and the outputs of all the cells are stored in ``model_output``.
        """
        from casas_web_portal.functions import _run_command, intersect_polygons

        grid = os.path.join(GRID_DIR, f"{self.weather}_grid_land.fgb")
        polygons = intersect_polygons(grid, self.geom)
        rundirs = []
        self.started = timezone.now()
        self.save(update_fields=["started"])
        for poly in polygons:
            x = poly["properties"]["x"]
            y = poly["properties"]["y"]
            txt_file = f"casas_{self.weather}_{x}_{y}.txt"
            gzip_file = os.path.join(settings.TXT_DIR, self.weather, f"{txt_file}.gz")
            rundir = os.path.join(
                settings.TXT_DIR, self.weather, f"{self.model}_{self.id}_{x}_{y}"
            )
            unzip_file = os.path.join(rundir, txt_file)
            os.makedirs(rundir, exist_ok=True)
            with gzip.open(gzip_file, "r") as f:
                with open(unzip_file, "wb") as out:
                    out.write(f.read())
            _run_command(
                [
                    os.path.join(SCRIPTS_DIR, self.model),
                    os.path.join(SCRIPTS_DIR, f"{self.model}.ini"),
                    str(self.start_date.month),
                    str(self.start_date.day),
                    str(self.start_date.year),
                    str(self.end_date.month),
                    str(self.end_date.day),
                    str(self.end_date.year),
                    str(GIS_OUTPUT_INTERVAL),
                    unzip_file,
                ],
                cwd=rundir,
            )
            os.remove(unzip_file)
            rundirs.append(rundir)
        if rundirs:
            archive_name = f"{self.id}.zip"
            with tempfile.TemporaryDirectory() as tmpdir:
                archive_path = os.path.join(tmpdir, archive_name)
                with zipfile.ZipFile(
                    archive_path, "w", zipfile.ZIP_DEFLATED
                ) as archive:
                    for rundir in rundirs:
                        for fname in sorted(os.listdir(rundir)):
                            archive.write(
                                os.path.join(rundir, fname),
                                arcname=os.path.join(os.path.basename(rundir), fname),
                            )
                with open(archive_path, "rb") as archive:
                    self.model_output.save(archive_name, File(archive), save=True)
        self.ended = timezone.now()
        self.save(update_fields=["ended"])
        return self.model_output
