from django.urls import path

from .views import index, add_new, credits, termofuse, map

urlpatterns = [
    path("", index),
    path("map", map),
    path("add", add_new),
    path("credits", credits),
    path("termofuse", termofuse)
]