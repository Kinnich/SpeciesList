import pandas as pd
import streamlit as st
from streamlit.components.v1 import html
from st_keyup import st_keyup
from streamlit_modal import Modal
from streamlit_image_select import image_select
from ai_util import get_animal_facts
from iNat_util import get_iNat_locations, get_iNat_species_count

# Set page config
page_title = 'Local Wildlife'
st.set_page_config(page_title=page_title, page_icon='🐾', layout='wide')

# Initialize session variables
if 'animal_class' not in st.session_state:
    st.session_state.animal_class = None

if 'place_id' not in st.session_state:
    st.session_state.place_id = None

# --- Search bar ---
st.markdown('##### Choose a location 🔎 🌎')
col1, col2, col3 = st.columns(3)
with col1:
    location = st_keyup('Enter region, county or city:', placeholder='ex: City of Austin')
    possible_locations = get_iNat_locations(location) # list of Location objects

with col2:
    best_match_loc = st.selectbox(
        'Choose the best match:',
        options=possible_locations,
        format_func=lambda x: x.name,
        help="If your location doesn't appear in the list, \
            try spelling out the entire name and the state abbreviation"
    )
    if best_match_loc:
        # Get the iNaturalist id for the location (needed to query the species lists)
        place_id = best_match_loc.id
        st.session_state.place_id = place_id

    with col3:
        animal_class = st.selectbox(
            'What class of animals are you interested in?',
            ['Mammalia', 'Amphibia', 'Reptilia', 'Aves', 'Insecta', 'Mollusca', 'Arachnida'],
            key="animal_class",
        )


# --- Main page --- 
# Will show images only once a location is entered in search bar
if best_match_loc and st.session_state.animal_class and st.session_state.place_id:
    
    st.subheader(f"{animal_class} in {best_match_loc.name}")
    
    species_list = get_iNat_species_count(place_id, animal_class)
    
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

        # Some records don't have a common name so use the scientific name instead
        df_short['taxon.preferred_common_name'].fillna(df_short['taxon.name'], inplace=True)

        number_species = len(df)
        st.markdown(f'{number_species} species have been observed')

        # TODO - cap the number we want to show on a page - or maybe no insects?
        img = image_select(
                label="Select an animal to learn more",
                images=df_short['taxon.default_photo.medium_url'].tolist(),
                captions=df_short['taxon.preferred_common_name'].tolist(),
                use_container_width=False,
                return_value='index'
            )

        if img:
            with st.sidebar:
                photo_link = df_short['taxon.default_photo.medium_url'].iloc[img]
                latin_name = df_short['taxon.name'].iloc[img]
                common_name = df_short['taxon.preferred_common_name'].iloc[img]
                num_observations = df_short['count'].iloc[img]
                st.header(common_name)
                st.image(photo_link, width=300)
                st.markdown(f"_{latin_name}_")
                st.text(f"{num_observations} observations")
                with st.spinner(f"Gathering info!"):
                    text = get_animal_facts(common_name)
                    st.markdown(text)


else:
    # Starting page is displayed only until user enters a location in search bar
    st.title('Identify local wildlife')
    st.markdown(
    """
    This is a simple app built on the iNaturalist and Pulze AI API's to:  
    1. List the wildlife in a given area and the number of observations recorded in iNaturalist
    2. Describe the tracks and signs made by an animal  

    This is meant to aid in learning basic tracking skills and develop a greater understanding and appreciation for what you see when you look around outside.  
    For more information about tracking checkout [Nature Tracking](https://naturetracking.com/)
    """
    )
