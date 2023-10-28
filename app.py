import streamlit as st
import requests
import pandas as pd
import time

# Helper functions to make API calls
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


# Set page config
apptitle = 'Species List'
st.set_page_config(page_title=apptitle, page_icon='random', layout='wide')

# Title the app
st.title('Find local wildlife')

# Initialize session variables
if 'best_loc_match' not in st.session_state:
    st.session_state.best_loc_match = None

if 'animal_group' not in st.session_state:
    st.session_state.animal_group = None

# Create sidebar functionality
with st.sidebar:
    st.markdown('## Choose a location and animal category')
    # TODO: add a note about how autocomplete works - and City of Austin is better than Austin for whatever reason
    # and Memphis Metropolitan Area works
    location = st.text_input('Enter location of interest - city, county, or well known landmark', '')
    
    if location:
        # Get list of valid locations and id's from iNaturalist given user input location
        possible_locations = get_iNat_locations(location)
        best_match_loc = st.selectbox(
            'Choose the best match:',
            options=possible_locations.keys(),
            key="best_loc_match",
            index=None,
        )
        # 55071 # Big Bend National Park
        if best_match_loc:
            # Get the iNaturalist id for the location (needed to query the species lists)
            place_id = possible_locations[best_match_loc]
            st.session_state.place_id = place_id

            # Set an animal group
            animal_group = st.selectbox(
                'What animal group are you interested in?',
                ['Mammalia', 'Amphibia', 'Reptilia', 'Aves', 'Insecta', 'Mollusca'],
                key="animal_group",
                index=None,
            )
# Main page displays table only once location and animal group are selected from sidebar
if st.session_state.best_loc_match and st.session_state.animal_group:

    st.subheader(f"{animal_group} in {st.session_state.best_loc_match}")
    
    species_list = get_iNat_species_count(place_id, animal_group)
    if species_list['total_results'] == 0:
        st.text(
            "Sorry there are no results. \n"
            "Try a different location or different location name i.e. 'City of Austin' instead of 'Austin'")

    else:
        data = species_list['results']
        normalized = pd.json_normalize(data)
        df = pd.DataFrame.from_dict(normalized)

        df_short = df[['taxon.preferred_common_name', 'taxon.name','count','taxon.wikipedia_url']].copy()
        df_short = df_short.rename(columns={
            'taxon.preferred_common_name': 'Common Name',
            'taxon.name': 'Latin Name',
            'count': 'Number of observations',
            'taxon.wikipedia_url': 'Wikipedia URL',

        })
        number_species = len(df)
        st.text(f'There are {number_species} species observed in this location')
        st.table(df_short)
else:
    st.write("not submitted")
# # TODO: make wiki urls in df hyperlinks

# TODO add optional downloads as csv or other?