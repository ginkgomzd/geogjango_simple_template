from __future__ import unicode_literals
from django.contrib.gis.db import models
from locations.models import *

# this is a file that will describe synthetic models
# it's possible that this will need to become subfolers
# with primitives and synthetics


class Location(models.Model):
    """This is a model for a Location, which has:
        :Name
        :Nickname
        :Address
        :Polygons

    The purpose of a Location is to make it possible to have different kinds of sub-locations,
    which we call Places and Localities.

    A place is defined by a Point Geometry and a Locality and is defined by Polygon or MultiPolygon
    geometry.

    """

    name = models.CharField(max_length=500)
    nickname = models.CharField(max_length=500)

    # foreign key to timezone

    timezone = models.ForeignKey(
        Timezone, on_delete=models.SET_DEFAULT, null=True, blank=True, default=None
    )

    # foreign key to GADM polygons

    gid_0 = models.ForeignKey(
        Country, on_delete=models.SET_DEFAULT, null=True, blank=True, default=None
    )
    gid_1 = models.ForeignKey(
        Admin_Level_1, on_delete=models.SET_DEFAULT, null=True, blank=True, default=None
    )
    gid_2 = models.ForeignKey(
        Admin_Level_2, on_delete=models.SET_DEFAULT, null=True, blank=True, default=None
    )
    gid_3 = models.ForeignKey(
        Admin_Level_3, on_delete=models.SET_DEFAULT, null=True, blank=True, default=None
    )
    gid_4 = models.ForeignKey(
        Admin_Level_4, on_delete=models.SET_DEFAULT, null=True, blank=True, default=None
    )
    gid_5 = models.ForeignKey(
        Admin_Level_5, on_delete=models.SET_DEFAULT, null=True, blank=True, default=None
    )

    def __str__(self):
        representative_string = f"{self.name}"
        return representative_string

    class Meta:
        abstract = True
        verbose_name = "location"
        verbose_name_plural = "locations"


class Place(Location):
    """
    This is a model for a Location that has a Point Geometry.
    Strictly speaking, you could get the point Geometry from the Address field, I guess.
    Let's not worry about that for now.
    """

    address = models.ForeignKey(
        United_States_Address,
        on_delete=models.SET_DEFAULT,
        null=True,
        blank=True,
        default=None,
    )
    geom = models.PointField(srid=4326, null=True, blank=True, default=None)

    class Meta:
        abstract = False
        verbose_name = "place"
        verbose_name_plural = "places"


class Locality(Location):
    """
    This is a model for a Location that has a Point Geometry.
    Strictly speaking, you could get the point Geometry from the Address field, I guess.
    Let's not worry about that for now.
    """

    geom = models.MultiPolygonField(srid=4326)

    class Meta:
        abstract = False
        verbose_name = "locality"
        verbose_name_plural = "localities"