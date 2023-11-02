import os
import openai
import streamlit as st

# Access the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = "https://api.pulze.ai/v1" # enter Pulze's URL


# url = "http://en.wikipedia.org/wiki/Raccoon"

prompt = """What signs can I use to track this animal?
    - What do the tracks look like?
    - Describe the scat
    - What feeding signs does this animal leave?
    - Where does the animal make its home/ bed/ nest/ den?
    - In which seasons is the animal active?
    Return response in html with no formating except 
    using these headings with <h4> tags: 
    Tracks, Scat, Feeding_signs, Home, Seasonal Activity
    """ 

@st.cache_data
def llm_summarize(animal: str) -> str:
    response = openai.ChatCompletion.create(
        model="pulze-v0",
        max_tokens=350,
        messages=[{
        "role": "user",
        "content": (prompt + animal),
        }],
    )
    return response['choices'][0]['message']['content']
