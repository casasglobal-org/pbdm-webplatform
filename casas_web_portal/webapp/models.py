from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _
# Create your models here.

CONTINENT = (
    ("EU", _("Europe")),
    ("AS", _("Asia")),
    ("AF", _("Africa")),
    ("NA", _("North America")),
    ("SA", _("South America")),
    ("OC", _("Oceania")),
)

PDBMS = (
    ("olive", _("Olive")),
    ("another", _("Another"))
)

WEATHERS = (
    ("era5", "AgERA5 v2.0"),
    ("cmip6", "NEX-GDDP-CMIP6 v2.0")
)


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
    continent = models.CharField(
        max_length=2, choices=CONTINENT, null=True, blank=True
    )

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

    class Meta():
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
