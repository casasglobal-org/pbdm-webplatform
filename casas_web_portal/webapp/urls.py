from django.urls import path

from .views import (
    index,
    add_new,
    credits,
    operation,
    termofuse,
    map,
    job_detail,
    process,
)

urlpatterns = [
    path("", index),
    path("map", map),
    path("add", add_new),
    path("credits", credits),
    path("termofuse", termofuse),
    path("process", process, name="process"),
    path("operation", operation, name="operation"),
    path("job/<int:job_id>", job_detail),
]
