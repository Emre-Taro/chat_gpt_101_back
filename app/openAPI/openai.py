import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY") # load env variable from .env file

def generate_openai_response(messages: list[dict], model: str = "gpt-4o-mini") -> str | dict:
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