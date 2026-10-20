from django.db import migrations


def register_multipolygon_column(apps, schema_editor):
    """Register general_job.geom as a MultiPolygon in the spatialite metadata.

    The spatialite triggers validate every write against geometry_columns,
    so the declared type has to be widened before the rows are converted.
    """
    connection = schema_editor.connection
    if connection.vendor != "sqlite":
        # PostGIS reads the column type from the catalog, which the ALTER in
        # 0002 already changed, and casts the stored values on the ALTER itself.
        return
    Job = apps.get_model("webapp", "Job")
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' "
            "AND name = 'geometry_columns'"
        )
        if not cursor.fetchone():
            # no spatialite metadata, nothing to register
            return
        cursor.execute(
            "UPDATE geometry_columns SET geometry_type = 6 "
            "WHERE f_table_name = %s AND f_geometry_column = %s",
            [Job._meta.db_table, Job._meta.get_field("geom").column],
        )


def wrap_job_polygons(apps, schema_editor):
    """Store the existing Polygon areas as MultiPolygon."""
    from django.contrib.gis.geos import GEOSGeometry, MultiPolygon

    Job = apps.get_model("webapp", "Job")
    using = schema_editor.connection.alias
    for job in Job.objects.using(using).all():
        geom = job.geom
        if geom is None or geom.empty or geom.geom_type != "Polygon":
            continue
        srid = geom.srid or 4326
        # rebuild from WKT: a Polygon read from a column typed as
        # MultiPolygon keeps the MultiPolygon python class and cannot be
        # wrapped as it is
        polygon = GEOSGeometry(geom.wkt)
        polygon.srid = srid
        job.geom = MultiPolygon(polygon)
        job.save(using=using, update_fields=["geom"])


class Migration(migrations.Migration):

    dependencies = [
        ("webapp", "0002_alter_job_geom"),
    ]

    operations = [
        migrations.RunPython(
            register_multipolygon_column, migrations.RunPython.noop
        ),
        migrations.RunPython(wrap_job_polygons, migrations.RunPython.noop),
    ]
