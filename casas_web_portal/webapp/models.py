import os
import glob
import geopandas as gpd
import subprocess
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from huey.contrib import djhuey as huey
from casas_web_portal.functions import _send_mail

# Create your models -------here.

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
    geom = models.PolygonField(
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

    class Meta(BaseDigi.Meta):
        db_table = "general_job"
        ordering = ["-created"]

    def __str__(self):
        output = f"{self.name} {self.model} {self.weather} - {self.start_date}/{self.end_date}"
        return smart_str(output)


@huey.task()
def run_pbdm_script(job_id):
    """Function to run the PBDM script for a given job

    Args:
        job_id (int): The job id
    """
    # Here you would add the code to run the PBDM script
    print(f"Running PBDM script for job {job_id}")
    job = Job.objects.get(id=job_id)
    job.started = models.DateTimeField(auto_now=True)
    job.save()
    _send_mail(
        "Job Started",
        f"Your job has started, you will receive an email when it will be finished.",
        job.user,
    )
    filepath = os.path.join(
        settings.STATIC_ROOT, "data", "{}_grid_land.fgb".format(job.weather)
    )
    points_gdf = gpd.read_file(filepath)
    points_within = points_gdf[points_gdf.geometry.within(job.geom)]
    txt_dir = os.path.join(settings.TXT_DIR, job.weather)
    files = []
    errors = []
    for point in points_within.itertuples():
        infiles = glob.glob(
            os.path.join(txt_dir, f"*_{point.attrs.col}_{point.attrs.row}.txt.gz")
        )
        files.extend(infiles)
        for infile in infiles:
            print(f"Processing file {infile} for job {job_id}")
            try:
                out = subprocess.run([], check=True, shell=True)
            except Exception as e:
                print(f"Error processing file {infile} for job {job_id}: {e}")
                errors.append((infile, str(e)))
            print(f"Finished processing file {infile} for job {job_id}")
            # Process the file (this is just a placeholder)
    job.ended = models.DateTimeField(auto_now=True)
    job.save()
    if len(errors) > 0:
        error_messages = "\n".join([f"{f}: {msg}" for f, msg in errors])
        _send_mail(
            "Job Completed with Errors",
            f"Your job with ID {job.id} has been completed but some errors occurred:\n{error_messages}\nYou can now check the maps selecting the variables of your interest on the following link https://{os.environ.get("APP_URL")}/job/{job.id}/",
            job.user,
        )
    else:
        _send_mail(
            "Job Completed",
            f"Your job has been completed. You can now create the maps selecting the variables of your interest on the following link https://{os.environ.get("APP_URL")}/job/{job.id}/",
            job.user,
        )


@receiver(post_save, sender=Job)
def create_run_analisys(sender, instance, created, **kwargs):
    """Signal to create the run analysis when a new job is created

    Args:
        sender (_type_): _description_
        instance (_type_): _description_
        created (_type_): _description_
    """
    if created:
        run_pbdm_script(instance.id)
