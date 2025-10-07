from django.contrib.gis import forms
from .models import Job

class BootstrapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
        })

class JobForm(BootstrapForm):
    geom = forms.PolygonField(srid=4326,)#  widget=forms.OSMWidget(attrs={"display_raw": True}))

    class Meta:
        model = Job
        fields = "__all__"