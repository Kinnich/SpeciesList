import openai
import streamlit as st


# API key stored in streamlit secrets
openai.api_key = st.secrets["pulzeai"]["OPENAI_API_KEY"]
openai.api_base = "https://api.pulze.ai/v1"


prompt = """What signs can I use to track this animal?
    - What do the tracks look like?
    - Describe the scat
    - What feeding signs does this animal leave?
    - Where does the animal make its home/ bed/ nest/ den?
    - In which seasons is the animal active?
    Return response in markdown with no formating except 
    using these as level 4 headings: 
    Tracks, Scat, Feeding_signs, Home, Seasonal Activity
    """ 

@st.cache_data(show_spinner=False)
def get_animal_facts(animal: str) -> str:
    """Use LLM's chat completion to get facts about a given animal"""
    response = openai.ChatCompletion.create(
        model="pulze-v0",
        max_tokens=350,
        messages=[{
        "role": "user",
        "content": (prompt + animal),
        }],
    )
    return response['choices'][0]['message']['content']
