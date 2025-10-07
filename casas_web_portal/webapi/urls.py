from rest_framework import routers

from .views import JobViewset

router = routers.DefaultRouter()
router.register(r"jobs", JobViewset, basename="jobs")