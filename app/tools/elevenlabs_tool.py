# app/tools/elevenlabs_tool.py
from elevenlabs.client import ElevenLabs
import os, tempfile

api_key = os.getenv("ELEVENLABS_API_KEY")

client = ElevenLabs(api_key=api_key)

def text_to_speech_tool(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb"):
    """Convert text to speech using ElevenLabs API."""
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    # Save to a temporary file
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    with open(tmp_file.name, "wb") as f:
        f.write(audio)
    return tmp_file.name
