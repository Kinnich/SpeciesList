import streamlit as st
from st_keyup import st_keyup
from streamlit_modal import Modal
import pandas as pd
from ai_util import llm_summarize
from iNat_util import get_iNat_locations, get_iNat_species_count, Location


# Set page config
apptitle = 'Species Tracker'
st.set_page_config(page_title=apptitle, page_icon='🐾', layout='wide')


# Title the app
st.title('Discover local wildlife')
st.divider()
st.markdown(
    """
    This is a simple app built on iNaturalist API and Pulze AI to:  
    1. List the wildlife observed in a given area  
    2. Describe the tracks and signs made by the animal  

    This is meant to aid in learning basic tracking skills and develop  
    a greater understanding for what you see when you look around outside.
    """
)

# Initialize session variables
if 'best_loc_match' not in st.session_state:
    st.session_state.best_loc_match = None

if 'animal_class' not in st.session_state:
    st.session_state.animal_class = None

if 'place_id' not in st.session_state:
    st.session_state.place_id = None

# Create sidebar functionality
with st.sidebar:
    st.markdown('## Choose a location and animal class')
    
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

# modal = Modal(key="Demo Key",title="test", padding=10, max_width='500')
# open_modal = st.button(label='button')
# if open_modal:
#     with modal.container():
#         st.markdown('testtesttesttesttesttesttesttest')
    
# Main page displays table only once location and animal group are selected from sidebar
if best_match_loc and st.session_state.animal_class and st.session_state.place_id:
    st.divider()
    st.markdown(
        """
        Here is a list of animals that have been observed in the location you chose.\n 
        Learn more about how to identify their tracks and other signs they leave on the landscape
        """
    ) 
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
    st.divider()
    st.write("To get started, choose a location on the sidebar!")

# TODO add optional downloads as csv or other?