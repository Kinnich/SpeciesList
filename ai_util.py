import os
import openai

# Access the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = "https://api.pulze.ai/v1" # enter Pulze's URL


# url = "http://en.wikipedia.org/wiki/Raccoon"

def llm_summarize(article: str) -> str:
    response = openai.ChatCompletion.create(
        model="pulze-v0",
        max_tokens=100,
        messages=[{
        "role": "user",
        "content": f"Summarize this article in 2-3 bullet points:{article}. Do not use complete sentences or use the animal name in bullet points."
        }],
    )
    return response['choices'][0]['message']['content']
