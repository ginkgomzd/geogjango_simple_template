from locations.models import *
from locations.serializers import *

from rest_framework import generics
from django.conf import settings

# geography things
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Transform

# utilities

from utilities import *
from rest_framework_gis.pagination import GeoJsonPagination


# logging

import logging

logger = logging.getLogger("django")


# Create your views here.
class Filtered_Place_List(generics.ListAPIView):

    # serializer for filtered results
    serializer_class = Place_Serializer

    # names of variables in url

    def get_queryset(self):

        # get params from url
        # Assuming EPSG:4326
        try:
            longitude = float(self.request.query_params.get("longitude"))
            latitude = float(self.request.query_params.get("latitude"))
            radius = Distance(m=float(self.request.query_params.get("radius")))
            epsg = int(
                self.request.query_params.get(
                    "epsg", settings.DEFAULT_PROJECTION_NUMBER
                )
            )
            logging.info(f"Received params: {longitude}, {latitude}, {radius}, {epsg}")
            # radius_in_degrees = distance_to_decimal_degrees(
            #     distance=radius, latitude=latitude
            # )
            reference_geom = Point((longitude, latitude), srid=epsg)
            logging.info(f"Made reference geom: {reference_geom}")

            reference_geom.transform(
                settings.PREFERRED_PROJECTION_FOR_US_DISTANCE_SEARCH
            )
            logging.info(f"Reprojected reference point: {reference_geom.srid}")

            queryset = (
                Place.objects.annotate(
                    distance_geom=Transform(
                        "geom", settings.PREFERRED_PROJECTION_FOR_US_DISTANCE_SEARCH
                    )
                )
                .filter(distance_geom__dwithin=(reference_geom, radius))
                .order_by("pk")
            )
            paginator = GeoJsonPagination()

            page = paginator.paginate_queryset(queryset, request)

            serializer = Place_Serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Exception as e:
            message = ""
            message += f"There was an error getting the radius results for Place: {e}"
            logging.error(message)
            queryset = None

        return queryset
