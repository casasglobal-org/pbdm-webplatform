from django.shortcuts import render, redirect

from .forms import JobForm

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
    return render(request, "map.html")

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