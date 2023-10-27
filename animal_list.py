import requests
import pandas as pd

location = input("Enter a location (city, county, or well known landmark like 'Big Bend National Park'): \n")
# 'big bend national park'

parameters = {
    'q': location
}
url = "https://api.inaturalist.org/v1/places/autocomplete"
response = requests.get(url, params=parameters)

print(response.json()['results'][0]['name'])
check = input("is that right? y/n:\n")
# IS THERE A WAY TO display a list and choose one from on the app?
if check == "y":
    place_id = response.json()['results'][0]['id']

# get place id and plug into api call
animal_groups = ['Animalia', 'Amphibia', 'Aves', 'Insecta', 'Mollusca', 'Reptilia']
animal_group = 'Mollusca'


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
# url = "http://www.inaturalist.org/observations/taxon_stats.json" # can't get all the results to list

response = requests.get(url, params=parameters)
data = response.json()['results']
print(len(data))

normalized = pd.json_normalize(data)
df = pd.DataFrame.from_dict(normalized)
df = df[['taxon.preferred_common_name','count','taxon.wikipedia_url']]
print(df)
# df.to_csv('animal_list.csv')