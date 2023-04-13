import requests
from requests.structures import CaseInsensitiveDict
import json
import os


def generate_image_from_text(prompt):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {os.environ['OPENAI_API_KEY']}"

    data = """
    {
        "model": "image-alpha-001",
        "prompt": "A large clocktower with ivy growing up its sides.",
        "num_images":1,
        "size":"1024x1024",
        "response_format":"url"
    }
    """

    data = data.replace("A large clocktower with ivy growing up its sides.", prompt)

    resp = requests.post("https://api.openai.com/v1/images/generations", headers=headers, data=data)

    if resp.status_code != 200:
        raise ValueError("Failed to generate image")

    response_text = json.loads(resp.text)
    return response_text['data'][0]['url']
