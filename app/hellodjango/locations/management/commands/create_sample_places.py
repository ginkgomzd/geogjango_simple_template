# Imports
# Generic Python Library Imports

import sys, os
import pathlib
import csv
from os.path import split

# Django Management Command Imports

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# custom functions and data

from locations.models import *

from utilities import *

# geography things
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import fromstr


# logging

import logging

logger = logging.getLogger("django")


class Command(BaseCommand):
    args = ""
    help = "Creates Location objects from AZ government data and uses the Nominatim API to geocode them"

    def handle(self, *args, **kwargs):

        # get command line specified options
        # container variables

        successes = []
        failures = []

        SAMPLE_LOCATIONS_CSV = (
            settings.TABULAR_DATA_SUBDIRECTORY
            / "pharmacies"
            / "geocoded_pharmacies.csv"
        )

        # start work
        try:
            message = "\n"
            message += "About to do the business"

            result = create_places_from_data_file(
                path_to_data_file=SAMPLE_LOCATIONS_CSV
            )

            successes.append(result)
        except Exception as e:
            message = "\n"
            message += f"There was an error at the management command level working on {message}: {e}"
            logger.error(message)
            failures.append(message)

        # count failures
        if len(failures) > 0:
            message = "\n FAILURE"
            message += f"\n The following models succeeded : {successes}"
            message += f"\n The following models failed : {failures}"

            logger.error(message)

        else:
            message = "\n SUCCESS"
            message += f"\n The following models succeeded : {successes}"
            message += f"\n The following models failed : {failures}"

            logger.info(message)


def create_places_from_data_file(path_to_data_file: pathlib.Path) -> bool:

    United_States_Address.objects.all().delete()
    Place.objects.all().delete()

    # container for bad addresses

    bad_locations = []

    # open the csv and create a DictReader

    try:
        inpath = pathlib.Path(path_to_data_file)

        with inpath.open("r", newline="\n", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            for row in reader:

                # field names
                # 'original_Pharmacy ID',
                # 'original_Pharmacy Name',
                # 'original_Pharmacy        Address 1',
                # 'original_Pharmacy City',
                # 'original_State',
                # 'original_Pharmacy Zip Code',
                # 'original_Pharmacy Phone Number',
                # 'lat',
                # 'lon',
                # 'formatted',
                # 'name',
                # 'housenumber',
                # 'street',
                # 'postcode',
                # 'suburb',
                # 'district',
                # 'city',
                # 'county',
                # 'state',
                # 'state_code',
                # 'country',
                # 'country_code',
                # 'confidence',
                # 'confidence_city_level',
                # 'confidence_street_level',
                # 'confidence_building_level',
                # 'attribution',
                # 'attribution_license',
                # 'attribution_url'

                # Get address fields

                split_address_raw = row["formatted"].split(",")
                split_address = list(map(str, split_address_raw))

                primary_number = row["housenumber"].strip()
                street_name = row["street"].strip()
                city_name = row["city"].strip()
                state_abbreviation = row["state_code"].strip()
                zip5 = row["postcode"].strip()

                # coordinates
                longitude = row["lon"].strip()
                latitude = row["lat"].strip()

                place_address = United_States_Address(
                    primary_number=primary_number.strip(),
                    street_name=street_name.strip(),
                    city_name=city_name,
                    state_abbreviation=state_abbreviation,
                    zip5=zip5,
                    longitude=longitude,
                    latitude=latitude,
                    geom=fromstr(f"POINT({longitude} {latitude})", srid=4326),
                )
                #                     message = ""
                #                     message += f"""
                #                     pn: {primary_number}, {len(primary_number)}; sn: {street_name}, {len(street_name)}
                #                     cn: {city_name}, {len(city_name)}; sa: {state_abbreviation}, {len(state_abbreviation)};
                #                     z5: {zip5}, {len(zip5)}; lng: {longitude}, {len(longitude)}; lat: {latitude}, {len(latitude)}
                # """
                #                     logging.info(message)
                place_address.save()
                #
                # get place name

                name = row["name"]
                if place_address:
                    new_place = Place(
                        name=name,
                        address=place_address,
                        geom=fromstr(f"POINT({longitude} {latitude})", srid=4326),
                    )
                    new_place.save()
                    message = ""
                    message += f"Place {name} created successfully."
                    logging.info(message)
                else:
                    message = ""
                    message += (
                        f"Place {name} could not be created because of address: {place_address}"
                        f""
                    )
                    logging.info(message)

    except Exception as e:
        message = "\n"
        message += f"There was an error creating location objects: {e}"
        logger.error(message)
        return False


def geocode_addresses_with_nominatim() -> bool:
    return True
