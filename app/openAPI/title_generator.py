import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_title_from_message(message: str) -> str:
    prompt = f"Can you make a brief title for this message?\n\n{message}"
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
        temperature=0.3,
        n=1,
        stop=None,
    )
    title = response.choices[0].message.content.strip()
    return title