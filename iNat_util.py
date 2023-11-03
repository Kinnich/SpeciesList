"""Module to hold all function calls to the INaturalist API"""
import requests
import pandas as pd
from dataclasses import dataclass
import streamlit as st

@dataclass
class Location:
    """Small dataclass to hold just the attributes needed
    from the the JSON-formatted iNaturalist API response"""
    name: str
    id: int
    place_type: int


def get_iNat_locations(location: str) -> list[Location]:
    """Submit a location to the iNaturalist/places endpoint to get a 
    list of possible matches with a corresponding id. Endpoint will autocomplete
    the string with locations in the database. Places may be countries, counties, cities,
    other municipal boundaries, points or well known landmarks. Filters out any results
    that are points and not polygons.
    """
    parameters = {
        'q': location,
        'order_by': 'area'
    }
    url = 'https://api.inaturalist.org/v1/places/autocomplete'
    response = requests.get(url, params=parameters)
    location_results = response.json()['results']
    return [
        Location(
            name=loc['display_name'],
            id=loc['id'],
            place_type=loc['place_type']
        ) for loc in location_results if loc['geometry_geojson'] is not None
    ]


def get_iNat_species_count(place_id: int, animal_group: str) -> dict:
    """Makes API call to iNaturalist/species_count endpoint to return
    a list of species with the number of research grade observations
    """
    parameters = {
        'rank': 'species',
        'iconic_taxa': animal_group,
        'quality_grade': 'research', # Research grade observations have been validated
        'place_id': place_id, # ex: Big Bend National Park = 55071
        'order': 'desc',
    }

    url = 'https://api.inaturalist.org/v1/observations/species_counts'
    response = requests.get(url, params=parameters)

    return response.json()
    

def clean_species_df(species_list: dict) -> pd.DataFrame:
    """
    Transform iNat API's JSON response to a cleaned dataframe with
    simple column names and filling in missing info
    """
    if species_list['total_results'] == 0:
        st.markdown("""**Sorry, there are no observations recorded in this location. 
                 Please try a different location.**""")
        
    else:
        data = species_list['results']
        normalized = pd.json_normalize(data)
        df = pd.DataFrame.from_dict(normalized)

        df_short = df[
            [
                'taxon.default_photo.medium_url',
                'taxon.preferred_common_name',
                'taxon.name',
                'count',
            ]
        ].copy()

        df_short.rename(
            columns = {
                'taxon.default_photo.medium_url': 'image',
                'taxon.preferred_common_name': 'common_name',
                'taxon.name': 'scientific_name',
            },
            inplace=True
        )
        # If common name is missing, use latin name
        df_short['common_name'].fillna(df_short['scientific_name'], inplace=True)

        # TODO: find a default photo to use if no photo available
    
        return df_short