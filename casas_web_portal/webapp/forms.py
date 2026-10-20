from django.contrib.gis import forms
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from .models import Job


class BootstrapFormMixin:
    """Add the Bootstrap 5 class matching each widget to the rendered input."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.HiddenInput):
                continue
            if isinstance(
                widget,
                (forms.CheckboxInput, forms.CheckboxSelectMultiple, forms.RadioSelect),
            ):
                css_class = "form-check-input"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_class = "form-select"
            else:
                css_class = "form-control"
            classes = widget.attrs.get("class", "").split()
            if css_class not in classes:
                classes.append(css_class)
            widget.attrs["class"] = " ".join(classes)


class BootstrapForm(BootstrapFormMixin, forms.ModelForm):
    pass


class DatePickerInput(forms.DateInput):
    """HTML5 date input, shows the browser date picker."""

    input_type = "date"


class JobGeomField(forms.MultiPolygonField):
    """A MultiPolygon field also accepting a single Polygon.

    The drawn areas are single polygons, they are wrapped into a
    MultiPolygon with one part before the MultiPolygon type check.
    """

    def to_python(self, value):
        geom = super().to_python(value)
        if geom is None or geom.geom_type != "Polygon":
            return geom
        srid = geom.srid
        geom = MultiPolygon(GEOSGeometry(geom.wkt))
        if srid:
            geom.srid = srid
        return geom


class JobForm(BootstrapForm):
    geom = JobGeomField(
        srid=4326,
    )  #  widget=forms.OSMWidget(attrs={"display_raw": True}))

    class Meta:
        model = Job
        fields = "__all__"
        widgets = {
            "start_date": DatePickerInput(format="%Y-%m-%d"),
            "end_date": DatePickerInput(format="%Y-%m-%d"),
        }


class OperationFileForm(BootstrapFormMixin, forms.Form):
    model = forms.ChoiceField(
        choices=[["andalusia", "Andalusia"], ["italia", "Italia"]]
    )
    file = forms.FileField()  # upload_to="operations/")
    separator = forms.CharField(
        max_length=255,
        help_text="The separator used in the file, for example: ',' for csv files and '\\t' for tsv files",
    )


class OperationFinalForm(BootstrapFormMixin, forms.Form):
    latitude = forms.IntegerField()
    longitude = forms.IntegerField()
    altitude = forms.IntegerField(
        help_text="The max altitude used, after this altitude the model will not be applied",
        required=False,
    )
    parameter = forms.ChoiceField(
        choices=[],
        help_text="The parameter to be used for the analysis",
    )
    interpolation = forms.ChoiceField(
        choices=[["nearest", "Nearest"], ["bilinear", "Bilinear"]]
    )
    points_number = forms.IntegerField(
        help_text="The number of points to be used for the interpolation",
        required=False,
    )
    legend = forms.CharField(
        max_length=255,
        help_text="The test for the legend to be used in the map",
        required=False,
    )
    color = forms.CharField(
        max_length=2550,
        help_text="RGB color as the following format: 'R:G:B-R:G:B-R:G:B...' where R, G and B are integers between 0 and 255",
        required=False,
    )
    crop = forms.CharField(
        max_length=255,
        help_text="The layer crop to be used for the analysis",
        required=False,
    )
    crop_value = forms.IntegerField(
        help_text="The value of the crop layer to be used for the analysis",
        required=False,
    )
    resolution = forms.IntegerField(
        min_value=1,
        max_value=3,
        initial=2,
        help_text="The resolution user for output png file (1: low, 2: medium, 3: high). Default is 2.",
    )
