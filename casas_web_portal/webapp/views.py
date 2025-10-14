from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed
from django.db.models import Q
from .forms import JobForm
from .models import Job

# Create your views here.


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
            # do something.
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
