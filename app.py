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
animal_group = st.sidebar.selectbox(
    'What animal group are you interested in?',
        ['Mammalia', 'Amphibia', 'Reptilia', 'Aves', 'Insecta', 'Mollusca']
)
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
df_short = df[['taxon.preferred_common_name', 'taxon.name','count','taxon.wikipedia_url']].copy()
df_short = df_short.rename(columns={
    'taxon.preferred_common_name': 'Common Name',
    'taxon.name': 'Latin Name',
    'count': 'Number of observations',
    'taxon.wikipedia_url': 'Wikipedia URL',

})
number_species = len(df)

st.subheader(f"{animal_group} in {place_id}")
st.text(f"There are {number_species} species observed in this location")
st.table(df_short)