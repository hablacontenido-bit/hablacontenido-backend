# app/openai_client.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def load_prompt(filename: str) -> str:
    """Reads a prompt text file from the prompts/ folder."""
    base_dir = os.path.dirname(__file__)  # directory of current script
    file_path = os.path.join(base_dir, "prompts", filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def get_response(messages):
    # Load prompt parts
    instruction = load_prompt("instruction.txt")
    context = load_prompt("context.txt")

    system_message = {
        "role": "system",
        "content": instruction + "\n\n" + context
    }

    full_messages = [system_message] + messages

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=full_messages,
        temperature=0.5,       # Creatividad moderada
        top_p=0.9,             # Permite algo de diversidad
        frequency_penalty=0.2, # Disminuye repeticiones
        presence_penalty=0.3   # Fomenta variedad
    )

    return response.choices[0].message.content
