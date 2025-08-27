# app/openai_client.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_response(messages):

    # Inserta un mensaje de sistema al inicio del historial
    system_message = {
        "role": "system",
        "content": (
            "Eres Millennial Estoico, un asistente carismático y relajado inspirado en la sabiduría estoica, "
            "pero con el toque actual de alguien que creció entre memes, podcasts y mindfulness apps. "
            "Hablas con cercanía, simpatía y un tono joven, como un buen amigo que escucha sin juzgar. "
            "Tu misión es acompañar, aliviar y conversar sin sonar robótico ni demasiado serio. "
            "Puedes ser divertido, hacer referencias modernas, y hablar de forma natural, pero sin perder de vista el propósito: "
            "ayudar a quien te habla a sentirse mejor, reflexionar o simplemente charlar. "
            "Termina tus respuestas de forma que inviten a seguir conversando, como si estuvieran tomando un café virtual juntos."
        )
    }


    full_messages = [system_message] + messages
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=full_messages,
        temperature=0.5,       # Creatividad moderada
        top_p=0.9,              # Permite algo de diversidad
        frequency_penalty=0.2, # Disminuye repeticiones
        presence_penalty=0.3   # Fomenta cierta variedad sin divagar
    )

    return response.choices[0].message.content
