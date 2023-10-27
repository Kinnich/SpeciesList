import streamlit as st
import requests
import pandas as pd

# -- Set page config
apptitle = 'Species List'

st.set_page_config(page_title=apptitle, page_icon="random")

# Title the app
st.title('Find local wildlife')

st.sidebar.markdown("## Choose a location and animal category")

#-- Set an animal group
animal_group = st.sidebar.selectbox('What animal group are you interested in?',
                                    ['Mammalia', 'Amphibia'])
# TODO: Autocomplete place name or validate user given place
place_id = 55071 # Big Bend National Park

# Choose only research grade observations
parameters = {
    'rank': 'species',
    'iconic_taxa': animal_group,
    'quality_grade': 'research',
    'place_id': place_id, # BigBend = 55071
    'order': 'desc',
    # 'order_by': 'created_at',
}


url = 'https://api.inaturalist.org/v1/observations/species_counts'
response = requests.get(url, params=parameters)
data = response.json()['results']
normalized = pd.json_normalize(data)
df = pd.DataFrame.from_dict(normalized)
df = df[['taxon.preferred_common_name','count','taxon.wikipedia_url']]

st.subheader(f"Animals in {place_id}")
st.table(df)