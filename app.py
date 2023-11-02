import streamlit as st
from st_keyup import st_keyup
from streamlit_modal import Modal
from streamlit.components.v1 import html
import pandas as pd
from ai_util import llm_summarize
from iNat_util import get_iNat_locations, get_iNat_species_count, Location

# Set page config
page_title = 'Local Wildlife'
st.set_page_config(page_title=page_title, page_icon='🐾', layout='wide')

# Initialize session variables
if 'best_loc_match' not in st.session_state:
    st.session_state.best_loc_match = None

if 'animal_class' not in st.session_state:
    st.session_state.animal_class = None

if 'place_id' not in st.session_state:
    st.session_state.place_id = None

# ---Sidebar---
with st.sidebar:
    st.markdown('## Choose a location')
    
    location = st_keyup('Enter region, county or city:', placeholder='ex: City of Austin')
    
    # Get list of valid locations from iNaturalist given user input location
    possible_locations = get_iNat_locations(location) # list of Location objects
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

        # Set an animal group
        animal_class = st.selectbox(
            'What class of animals are you interested in?',
            ['Mammalia', 'Amphibia', 'Reptilia', 'Aves', 'Insecta', 'Mollusca'],
            key="animal_class",
        )

# ---Main page --- 
# Will display table only once location and animal group are selected from sidebar
if best_match_loc and st.session_state.animal_class and st.session_state.place_id:
    st.subheader(f"{animal_class} in {best_match_loc.name}")
    
    species_list = get_iNat_species_count(place_id, animal_class)
    
    if species_list['total_results'] == 0:
        st.markdown("""**Sorry, there are no observations recorded in this location. 
                 Please try a different location or the county.**""")
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
        st.markdown(f'There have been {number_species} species observed in this location')
        
        # Create container to hold the form with selectbox
        container = st.container()
        
        # Display data in interactive df
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

        with container:
            # Get tracking info for a selected animal - using a 'select box' in a 'form' so that
            # the popup box will close and not freeze as it does using only the select box
            with st.form('animal_select'):
                animal = st.selectbox(
                    'Select an animal to learn how to identify their tracks and sign:',
                    options=df_short['taxon.preferred_common_name'].tolist(),
                    )
                submitted = st.form_submit_button("Tell me more!")

            if submitted:
                photo_link = df_short[df_short['taxon.preferred_common_name'] == animal]['taxon.default_photo.medium_url'].iloc[0]
                latin_name = df_short[df_short['taxon.preferred_common_name'] == animal]['taxon.name'].iloc[0]

                # Create and format the popup window
                modal = Modal(key=f"{animal}",title=f"{animal}", padding=10, max_width='650')
                with modal.container():
                    col1, col2 = st.columns(2, gap="small")
                    with col1:
                        st.image(photo_link, width=300)
                        st.markdown(f"_{latin_name}_")
                    with col2:
                        with st.spinner(f"Gathering info!"):
                            text = llm_summarize(animal)
                            html(text, height=300, scrolling=True, width=300)


else:
    st.title('Identify local wildlife!')
    st.markdown(
    """
    This is a simple app built on the iNaturalist and Pulze AI API's to:  
    1. List the wildlife in a given area and the number of observations recorded in iNaturalist
    2. Describe the tracks and signs made by an animal  

    This is meant to aid in learning basic tracking skills and develop a greater understanding and appreciation for what you see when you look around outside.  
    For more information about tracking I highly recommend checking out [Nature Tracking](https://naturetracking.com/)
    """
    )
    st.divider()
    st.write("⬅️ To get started, choose a location in the sidebar!")

# TODO add optional downloads as csv or other?