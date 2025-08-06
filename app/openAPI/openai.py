import os
import openai
import base64
from typing import Union, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") # load env variable from .env file

def generate_openai_response(messages: list[dict], model: str = "gpt-4o") -> str | dict:
    """
    Generate a response from OpenAI's API based on the provided messages.
    
    :param messages: List of message dictionaries to send to the OpenAI API.
    :param model: The model to use for generating the response.
    :return: The response from OpenAI's API.
    """
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating OpenAI response: {e}")
        return {"error": str(e)}

def create_vision_message(content: str, image_path: str) -> dict:
    """
    Create a vision message with image for OpenAI's vision API.
    
    :param content: The text content/prompt for the image
    :param image_path: Path to the image file
    :return: Message dictionary with image data
    """
    try:
        # Read and encode the image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        return {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": content
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        }
    except Exception as e:
        print(f"Error creating vision message: {e}")
        return {"error": str(e)}

def generate_openai_response_with_vision(messages: list[dict], model: str = "gpt-4o") -> str | dict:
    """
    Generate a response from OpenAI's vision API based on the provided messages with images.
    
    :param messages: List of message dictionaries to send to the OpenAI API.
    :param model: The model to use for generating the response (should support vision).
    :return: The response from OpenAI's API.
    """
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating OpenAI vision response: {e}")
        return {"error": str(e)}