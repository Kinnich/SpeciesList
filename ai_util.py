import os
import openai

# Access the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = "https://api.pulze.ai/v1" # enter Pulze's URL


# url = "http://en.wikipedia.org/wiki/Raccoon"

prompt = """Read this wiki page and give 3 short bullet points:
    - an interesting fact about animal
    - where on the landscape is it most often found?
    - what it eats
    """ 

def llm_summarize(article: str) -> str:
    response = openai.ChatCompletion.create(
        model="pulze-v0",
        max_tokens=100,
        messages=[{
        "role": "user",
        "content": (prompt + article),
        }],
    )
    return response['choices'][0]['message']['content']
