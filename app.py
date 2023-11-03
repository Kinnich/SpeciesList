import pandas as pd
import streamlit as st
from streamlit.components.v1 import html
from st_keyup import st_keyup
from streamlit_image_select import image_select
from ai_util import get_animal_facts
from iNat_util import get_iNat_locations, get_iNat_species_count, clean_species_df

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
            'Choose an animal class:',
            ['Mammalia', 'Amphibia', 'Reptilia', 'Aves', 'Insecta', 'Mollusca', 'Arachnida'],
            key="animal_class",
        )


# --- Main page --- 
# Will show images only once a location is entered in search bar
if best_match_loc and st.session_state.animal_class and st.session_state.place_id:
    
    st.subheader(f"{animal_class} in {best_match_loc.name}")
    
    # Call iNat API
    species_list = get_iNat_species_count(place_id, animal_class)
    species_df = clean_species_df(species_list)
    
    # Format records from df as a list of dicts, with column names as keys
    records = species_df.to_dict('records')

    number_species = len(species_df)
    st.markdown(f'{number_species} species observed')

    # TODO - cap the number we want to show on a page - or maybe no insects?
    img = image_select(
            label="Select an animal to learn more",
            images=species_df['image'].tolist(),
            captions=species_df['common_name'].tolist(),
            use_container_width=False,
            return_value='index'
        )
    # --- Sidebar --- pops up to display animal image and info
    if img:
        record = records[img]
        with st.sidebar:
            st.header(record['common_name'])
            st.image(record['image'], width=300)
            st.markdown(f"_{record['scientific_name']}_")
            st.text(f"{record['count']} observations")
            
            # Call Pulze to generate fun facts! This takes a while...
            with st.spinner(f"Tracking down info!"):
                text = get_animal_facts(record['common_name'])
                st.markdown(text)

else:
    # Starting page is displayed at start of session and then only until user enters a location in search bar
    st.title('Identify local wildlife')
    st.markdown(
    """
    This is a simple app built on the iNaturalist and Pulze AI API's to:  
    1. Show what wildlife has been observed in an area
    2. Describe the tracks and signs made by an animal  

    This is meant to aid in learning basic tracking skills and develop a greater understanding and appreciation for what you see when you look around outside.  
    For more information about tracking wildlife, checkout [Nature Tracking](https://naturetracking.com/)
    """
    )
