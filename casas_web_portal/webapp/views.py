import os
import gzip
import tempfile
import zipfile
from django.conf import settings
from django.core.files import File
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
SCRIPTS_DIR = os.path.join(settings.BASE_DIR, "scripts")
DATA_DIR = os.path.join(MAIN_DIR, "static", "data")
GIS_OUTPUT_INTERVAL = 30


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
        formset_layer = JobForm(auto_id="layer_%s")
        if request.user.is_anonymous:
            jobs = Job.objects.filter(is_public=True)
        else:
            jobs = Job.objects.filter(Q(user=request.user) | Q(is_public=True))
    return render(
        request,
        "map.html",
        {"formset": formset, "formset_layer": formset_layer, "jobs": jobs, "msg": None},
    )


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
                request,
                "operation.html",
                {
                    "formset": formset,
                    "msg": "Invalid form",
                    "button": "Next step",
                },
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
            job = formset.save()
            weather = formset.cleaned_data["weather"]
            model = formset.cleaned_data["model"]
            start_date = formset.cleaned_data["start_date"]
            end_date = formset.cleaned_data["end_date"]
            if weather == "era5":
                grid = os.path.join(DATA_DIR, "era5_grid_land.fgb")
            elif weather == "cmip6":
                grid = os.path.join(DATA_DIR, "cmip6_grid_land.fgb")
            polygons = intersect_polygons(grid, formset.cleaned_data["geom"])
            rundirs = []
            for poly in polygons:
                x = poly["properties"]["x"]
                y = poly["properties"]["y"]
                txt_file = f"casas_{weather}_{x}_{y}.txt"
                gzip_file = os.path.join(settings.TXT_DIR, weather, f"{txt_file}.gz")
                unzip_file = os.path.join(settings.TXT_DIR, weather, txt_file)
                rundir = os.path.join(settings.TXT_DIR, weather, f"{model}_{x}_{y}")
                os.makedirs(rundir, exist_ok=True)
                with gzip.open(gzip_file, "r") as f:
                    with open(unzip_file, "wb") as out:
                        out.write(f.read())
                # argv1 = SCRIPTS_DIR/<model> — script name identical to the model choice (olive)
                # argv2 = SCRIPTS_DIR/<model>.ini (setup file)
                # dates passed as month/day/year
                # argv8 = GIS_OUTPUT_INTERVAL = 30 (monthly, per your choice)
                # argv9 = full path of the unzipped weather txt
                # each cell runs in its own txt/<weather>/<model>_<x>_<y>/ dir (per your choice), cwd=rundir
                _run_command(
                    [
                        os.path.join(SCRIPTS_DIR, model),
                        os.path.join(SCRIPTS_DIR, f"{model}.ini"),
                        str(start_date.month),
                        str(start_date.day),
                        str(start_date.year),
                        str(end_date.month),
                        str(end_date.day),
                        str(end_date.year),
                        str(GIS_OUTPUT_INTERVAL),
                        unzip_file,
                    ],
                    cwd=rundir,
                )
                os.remove(unzip_file)
                rundirs.append(rundir)
            if rundirs:
                archive_name = f"{job.id}.zip"
                with tempfile.TemporaryDirectory() as tmpdir:
                    archive_path = os.path.join(tmpdir, archive_name)
                    with zipfile.ZipFile(
                        archive_path, "w", zipfile.ZIP_DEFLATED
                    ) as archive:
                        for rundir in rundirs:
                            for fname in sorted(os.listdir(rundir)):
                                archive.write(
                                    os.path.join(rundir, fname),
                                    arcname=os.path.join(
                                        os.path.basename(rundir), fname
                                    ),
                                )
                    with open(archive_path, "rb") as archive:
                        job.model_output.save(archive_name, File(archive), save=True)
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
