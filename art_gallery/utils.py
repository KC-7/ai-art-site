# import requests
import os
from requests import post
from requests.structures import CaseInsensitiveDict
from json import loads


def generate_image_from_text(prompt):
    """
    Generates an image from a text prompt using OpenAI's API.

    'prompt' - The text prompt to generate the image from.
    'return' - The URL of the generated image.
    'ValueError' - If the API request is not successful.
    """
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {os.environ['OPENAI_API_KEY']}"

    # Data to send to API
    data = """
    {
        "prompt": "A large clocktower with ivy growing up its sides.",
        "num_images":1,
        "size":"1024x1024",
        "response_format":"url"
    }
    """

    # Updates the prompt to the users specified input
    data = data.replace(
        "A large clocktower with ivy growing up its sides.", prompt
    )

    # Makes the API request by sending the updated data
    resp = post(
        "https://api.openai.com/v1/images/generations",
        headers=headers,
        data=data
    )

    # Checks if request is successful, if not it raises a ValueError
    if resp.status_code != 200:
        raise ValueError("Failed to generate image")

    # Extracts the image url from the response if successful
    response_text = loads(resp.text)
    return response_text['data'][0]['url']
