from django.contrib.gis.geos import GEOSException, GEOSGeometry, MultiPolygon
from django.utils.translation import gettext as _
from rest_framework import serializers

from webapp.models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        #fields = '__all__'
        exclude = ["image",]

    def validate_geom(self, value):
        """Return a MultiPolygon for Job.geom.

        The map sends either a drawn Polygon or a world feature that may be
        a MultiPolygon. Job.geom is a MultiPolygonField, so a single Polygon
        is rebuilt from its WKT and wrapped into a one part MultiPolygon.
        """
        try:
            geom = value if isinstance(value, GEOSGeometry) else GEOSGeometry(value)
        except (GEOSException, ValueError, TypeError) as err:
            raise serializers.ValidationError(
                _("The area of interest is not a valid geometry: %(error)s")
                % {"error": err}
            )
        srid = geom.srid or 4326
        if geom.empty:
            raise serializers.ValidationError(
                _("The area of interest must be a non empty polygon")
            )
        if geom.geom_type == "Polygon":
            # rebuild from WKT: a Polygon read from a MultiPolygon column
            # keeps the MultiPolygon python class and cannot be wrapped
            geom = MultiPolygon(GEOSGeometry(geom.wkt))
        elif geom.geom_type != "MultiPolygon":
            raise serializers.ValidationError(
                _("The area of interest must be a polygon")
            )
        geom.srid = srid
        return geom
