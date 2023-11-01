import streamlit as st
from st_keyup import st_keyup
import pandas as pd
from ai_util import llm_summarize
from iNat_util import get_iNat_locations, get_iNat_species_count


# Set page config
apptitle = 'Species Tracker'
st.set_page_config(page_title=apptitle, page_icon='🐾', layout='wide')

# Title the app
st.title('Find local wildlife')

# Initialize session variables
if 'best_loc_match' not in st.session_state:
    st.session_state.best_loc_match = None

if 'animal_class' not in st.session_state:
    st.session_state.animal_class = None

# Create sidebar functionality
with st.sidebar:
    st.markdown('## Choose a location and animal category')
    # TODO: add a note about how autocomplete works - and City of Austin is better than Austin for whatever reason
    # and Memphis Metropolitan Area works
    location = st_keyup('Enter location of interest - city, county, or well known landmark', '')
    # if location:
        # Get list of valid locations and id's from iNaturalist given user input location
    possible_locations = get_iNat_locations(location)
    best_match_loc = st.selectbox(
        'Choose the best match:',
        options=possible_locations.keys(),
        key="best_loc_match",
        # index=None,
    )

    if best_match_loc:
        # Get the iNaturalist id for the location (needed to query the species lists)
        place_id = possible_locations[best_match_loc]
        st.session_state.place_id = place_id

        # Set an animal group
        animal_class = st.selectbox(
            'What class of animals are you interested in?',
            ['Mammalia', 'Amphibia', 'Reptilia', 'Aves', 'Insecta', 'Mollusca'],
            key="animal_class",
            # index=None,
        )
# Main page displays table only once location and animal group are selected from sidebar
if st.session_state.best_loc_match and st.session_state.animal_class:

    st.subheader(f"{animal_class} in {st.session_state.best_loc_match}")
    
    species_list = get_iNat_species_count(place_id, animal_class)
    if species_list['total_results'] == 0:
        st.text(
            "Sorry there are no results. \n"
            "Try a different location or different location name i.e. 'City of Austin' instead of 'Austin'")

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

        number_species = len(df)
        st.text(f'There are {number_species} species observed in this location')

        st.dataframe(
            df_short,
            column_config={
                'taxon.default_photo.medium_url': st.column_config.ImageColumn(label='Image', width='small'),
                'taxon.preferred_common_name': 'Common Name',
                'taxon.name': 'Latin Name',
                'count': st.column_config.NumberColumn(label='Observations', width='medium'),
            },
            hide_index=True,
        )

        # Get tracking info for a selected animal
        animal = st.selectbox('Select an animal to learn more about', options=df_short['taxon.preferred_common_name'].tolist())
        photo_link = df_short[df_short['taxon.preferred_common_name'] == animal]['taxon.default_photo.medium_url'].iloc[0]
        latin_name = df_short[df_short['taxon.preferred_common_name'] == animal]['taxon.name'].iloc[0]
        col1, col2 = st.columns(2)
        with col1:
            st.image(photo_link)
            st.markdown(f"_{latin_name}_")
        
        with col2:
            col2.write(llm_summarize(animal))
else:
    st.write("Choose a location on the sidebar")

# TODO add optional downloads as csv or other?