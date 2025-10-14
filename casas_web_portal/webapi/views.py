from django.utils.translation import gettext as _
from django.db.models import Q

from rest_framework import permissions, viewsets
from rest_framework.response import Response

from casas_web_portal.permissions import get_permissions_class
from webapp.models import Job

from .serializers import JobSerializer

# Create your views here.


class JobViewset(viewsets.ModelViewSet):
    model = Job
    serializer_class = JobSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # Get the permissions class based on the action
        return get_permissions_class(self.action)

    def get_queryset(self):
        if self.request.method in ["GET", "RETRIEVE"]:
            return Job.objects.none()
        elif self.request.method == "DELETE":
            jobid = int(self.request.get_full_path().split("/")[-2])
            return Job.objects.filter(id=jobid)
        elif self.request.method == "PUT":
            if hasattr(self.request, "data"):
                job_id = self.request.data["job"]
                return Job.objects.filter(field=job_id)
            else:
                jobid = int(self.request.get_full_path().split("/")[-2])
                return Job.objects.filter(id=jobid)

    def list(self, request, pk=None):
        if request.user.is_superuser:
            data = Job.objects.all()
        elif request.user.is_anonymous:
            data = Job.objects.filter(is_public=True)
        else:
            data = Job.objects.filter(Q(user=request.user) or Q(is_public=True))
        usedserializer = self.get_serializer_class()
        if pk:
            try:
                indata = data.get(id=pk)
            except Exception:
                raise NotFound(_(f"No visible jobs with id {pk}"))
            seri = usedserializer(indata, context={"request": request})
        else:
            seri = usedserializer(data, many=True, context={"request": request})
        return Response(seri.data)

    def retrieve(self, request, pk):
        return self.list(request, pk)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
