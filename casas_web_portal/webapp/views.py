import os
import gzip
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse
from casas_web_portal.functions import write_inmemory_file
from casas_web_portal.functions import _run_command
from casas_web_portal.functions import intersect_polygons
from .forms import JobForm
from .forms import OperationFileForm
from .forms import OperationFinalForm
from .models import Job

# Create your views here.
MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(MAIN_DIR, "scripts")
DATA_DIR = os.path.join(MAIN_DIR, "static", "data")


def index(request):
    """Function to render the index page

    Args:
        request (_type_): _description_
    """
    return render(request, "index.html")


def map(request):
    """Function to render the map page

    Args:
        request (_type_): _description_
    """
    if request.method == "POST":
        return HttpResponseNotAllowed()
    else:
        formset = JobForm()
        if request.user.is_anonymous:
            jobs = Job.objects.filter(is_public=True)
        else:
            jobs = Job.objects.filter(Q(user=request.user) or Q(is_public=True))
    return render(request, "map.html", {"formset": formset, "jobs": jobs, "msg": None})


def process(request):
    """Function to use existing model to be used in fixed area

    Args:
        request (obj): the request
    """
    initial = {
        "file": request.session.get("file", None),
        "model": request.session.get("model", None),
    }
    formset = OperationFileForm(request.POST or None, initial=initial)
    if request.method == "POST":
        formset = OperationFileForm(request.POST, request.FILES)
        if formset.is_valid():
            # do something.
            file_path = write_inmemory_file(formset.cleaned_data["file"])
            request.session["file"] = file_path
            request.session["model"] = formset.cleaned_data["model"]
            request.session["separator"] = formset.cleaned_data["separator"]
            return HttpResponseRedirect(reverse("operation"))
        else:
            return render(
                request, "operation.html", {"formset": formset, "msg": "Invalid form"}
            )
    else:
        return render(
            request,
            "operation.html",
            {"formset": formset, "msg": None, "button": "Next step"},
        )


def operation(request):
    """Function to render the operation page

    Args:
        request (obj): the request
    """
    analisys_model = request.session.get("model", None)
    infile = request.session.get("file", None)
    separator = request.session.get("separator", None)
    header = None
    if infile:
        with open(infile, "r") as f:
            lines = f.readlines()
            header = lines[0].strip().split(separator.replace("\\t", "\t"))
    lat = None
    long = None
    methods = []
    if header:
        if "latitude" in header:
            lat = header.index("latitude")
        elif "lat" in header:
            lat = header.index("lat")
        elif "y" in header:
            lat = header.index("y")
        elif "Lat" in header:
            lat = header.index("Lat")
        if "longitude" in header:
            long = header.index("longitude")
        elif "lon" in header:
            long = header.index("lon")
        elif "x" in header:
            long = header.index("x")
        elif "Long" in header:
            long = header.index("Long")
        methods = [[i, i] for i in header]
        methods.insert(0, ["", "None"])
    if request.method == "POST":
        formset = OperationFinalForm(request.POST)
        formset.fields["parameter"].choices = methods
        if formset.is_valid():
            # do something.

            data = formset.cleaned_data
            print(analisys_model, infile, data)
            # execute grass code here
            stdout, stderr = _run_command(
                ["grass", location_path, "--exec", script_path]
            )
            return HttpResponseRedirect(reverse("map"))
        else:
            return render(
                request,
                "operation.html",
                {
                    "formset": formset,
                    "msg": "Invalid form",
                    "button": "Execute operation",
                },
            )
    else:
        initial = {"latitude": lat, "longitude": long, "parameter": methods}
        formset = OperationFinalForm(initial=initial)
        formset.fields["parameter"].choices = methods
        return render(
            request,
            "operation.html",
            {
                "formset": formset,
                "msg": None,
                "button": "Execute operation",
            },
        )


def add_new(request):
    """Views to add a new job

    Args:
        request (obj): The HTTP request

    Returns:
        _type_: _description_
    """
    if request.method == "POST":
        formset = JobForm(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            weather = formset.cleaned_data["weather"]
            start_date = formset.cleaned_data["start_date"]
            start_date_split = start_date.split("-")
            end_date = formset.cleaned_data["end_date"]
            end_date_split = end_date.split("-")
            if weather == "era5":
                grid = os.path.join(DATA_DIR, "era5_grid_land.fgb")
            elif weather == "cmip6":
                grid = os.path.join(DATA_DIR, "cmip6_grid_land.fgb")
            polygons = intersect_polygons(grid, formset.cleaned_data["geom"])
            for poly in polygons:
                # do something.
                txt_file = f"casas_{weather}_{poly['properties']['x']}_{poly['properties']['y']}.txt"
                gzip_file = os.path.join(
                    settings["DATA_DIR"], weather, f"{txt_file}.gz"
                )
                unzip_file = os.path.join(settings["TXT_DIR"], weather, txt_file)
                with gzip.open(gzip_file, "r") as f:
                    with open(unzip_file, "wb") as out:
                        out.write(f.read())
                _run_command(
                    [
                        TODO,
                        TODO,
                        start_date_split[0],
                        start_date_split[1],
                        start_date_split[2],
                        end_date_split[0],
                        end_date_split[1],
                        end_date_split[2],
                        TODO,
                        txt_file,
                    ]
                )
                os.remove(unzip_file)
            return redirect("/")
    else:
        formset = JobForm()
    return render(request, "add.html", {"formset": formset})


def credits(request):
    """Function to render the index page

    Args:
        request (_type_): _description_
    """
    return render(request, "credits.html")


def termofuse(request):
    """Function to render the index page

    Args:
        request (_type_): _description_
    """
    return render(request, "termofuse.html")


def job_detail(request, job_id):
    """Function to render the job detail page

    Args:
        request (_type_): _description_
        job_id (int): The job id
    """
    job = Job.objects.get(id=job_id)
    return render(request, "job_detail.html", {"job": job})
