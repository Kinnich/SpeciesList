import streamlit as st
import requests
import pandas as pd
import time

def validate_location(loc: str) -> dict:
    parameters = {
        'q': location
    }
    url = 'https://api.inaturalist.org/v1/places/autocomplete'
    response = requests.get(url, params=parameters)
    location_results = response.json()['results']
    return {loc['display_name']: loc['id'] for loc in location_results}


# -- Set page config
apptitle = 'Species List'
st.set_page_config(page_title=apptitle, page_icon='random', layout='wide')

# Title the app
st.title('Find local wildlife')

if 'best_loc_match' not in st.session_state:
    st.session_state.best_loc_match = None

if 'animal_group' not in st.session_state:
    st.session_state.animal_group = None

with st.sidebar:
    st.markdown('## Choose a location and animal category')
    # TODO: add a note about how autocomplete works - and City of Austin is better than Austin for whatever reason
    # and Memphis Metropolitan Area works
    location = st.text_input('Enter location of interest - city, county, or well known landmark', '')
    
    if location:
        possible_locations = validate_location(location)
        best_match_loc = st.selectbox(
            'Choose the best match:',
            options=possible_locations.keys(),
            key="best_loc_match",
            index=None,
        )
        # 55071 # Big Bend National Park
        if best_match_loc:
            place_id = possible_locations[best_match_loc]
            st.session_state.place_id = place_id

            #-- Set an animal group
            animal_group = st.selectbox(
                'What animal group are you interested in?',
                ['Mammalia', 'Amphibia', 'Reptilia', 'Aves', 'Insecta', 'Mollusca'],
                key="animal_group"
            )

if st.session_state.best_loc_match and st.session_state.animal_group:

    # Choose only research grade observations
    parameters = {
        'rank': 'species',
        'iconic_taxa': animal_group,
        'quality_grade': 'research',
        'place_id': st.session_state.place_id, # BigBend = 55071
        'order': 'desc',
        # 'order_by': 'created_at',
    }


    url = 'https://api.inaturalist.org/v1/observations/species_counts'
    response = requests.get(url, params=parameters)

    st.subheader(f"{animal_group} in {st.session_state.best_loc_match}")

    if response.json()['total_results'] == 0:
        st.text(
            "Sorry there are no results. \n"
            "Try a different location or different location name i.e. 'City of Austin' instead of 'Austin'")

    else:
        data = response.json()['results']
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