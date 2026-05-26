from django.contrib.gis import forms
from .models import Job


class BootstrapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({"class": "form-control"})


class JobForm(BootstrapForm):
    geom = forms.PolygonField(
        srid=4326,
    )  #  widget=forms.OSMWidget(attrs={"display_raw": True}))

    class Meta:
        model = Job
        fields = "__all__"


class OperationFileForm(forms.Form):
    model = forms.ChoiceField(
        choices=[["andalusia", "Andalusia"], ["italia", "Italia"]]
    )
    file = forms.FileField()  # upload_to="operations/")
    separator = forms.CharField(
        max_length=255,
        help_text="The separator used in the file, for example: ',' for csv files and '\\t' for tsv files",
    )


class OperationFinalForm(forms.Form):
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
