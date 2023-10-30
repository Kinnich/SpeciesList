"""Module to hold all function calls to the INaturalist API"""
import requests


def get_iNat_locations(location: str) -> dict:
    """Submit a location to the iNaturalist/places endpoint to get a 
    list of possible matches with a corresponding id. Endpoint will autocomplete
    the string with locations in the database. Places may be countries, counties, cities,
    other municipal boundaries, points or well known landmarks. 
    """
    parameters = {
        'q': location
    }
    url = 'https://api.inaturalist.org/v1/places/autocomplete'
    response = requests.get(url, params=parameters)
    location_results = response.json()['results']
    return {loc['display_name']: loc['id'] for loc in location_results}

def get_iNat_species_count(place_id: int, animal_group: str) -> dict:
    """Makes API call to iNaturalist/species_count endpoint to return
    a list of species with the number of observations
    """
    # Choose only research grade observations
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
