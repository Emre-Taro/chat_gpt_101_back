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

def generate_openai_response_with_vision(messages: List[Dict[str, Any]], model: str = "gpt-4o") -> Union[str, Dict[str, str]]:
    """
    Generate a response from OpenAI's API with vision capabilities (image processing).
    
    :param messages: List of message dictionaries that can include text and image content.
    :param model: The model to use for generating the response (default: gpt-4o).
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
        print(f"Error generating OpenAI response with vision: {e}")
        return {"error": str(e)}

def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string for OpenAI API.
    
    :param image_path: Path to the image file.
    :return: Base64 encoded string of the image.
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return ""

def create_vision_message(content: str, image_path: str = None) -> Dict[str, Any]:
    """
    Create a message with vision capabilities for OpenAI API.
    
    :param content: Text content of the message.
    :param image_path: Optional path to an image file to include.
    :return: Message dictionary formatted for OpenAI API.
    """
    message = {
        "role": "user",
        "content": []
    }
    
    # Add text content
    if content:
        message["content"].append({
            "type": "text",
            "text": content
        })
    
    # Add image content if provided
    if image_path:
        base64_image = encode_image_to_base64(image_path)
        if base64_image:
            # Determine the correct MIME type based on file extension
            file_extension = os.path.splitext(image_path)[1].lower()
            mime_type = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }.get(file_extension, 'image/jpeg')
            
            message["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}"
                }
            })
    
    return message