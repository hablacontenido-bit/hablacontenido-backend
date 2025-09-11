# app/agents.py
from autogen import AssistantAgent, UserProxyAgent, register_function
from app.tools.elevenlabs_tool import text_to_speech_tool
from app.openai_client import get_response

# Register the ElevenLabs function as a tool
register_function(
    text_to_speech_tool,
    name="text_to_speech",
    description="Generate speech from text using ElevenLabs API"
)

# Assistant Agent
assistant = AssistantAgent(
    name="assistant",
    llm_config={
        "model": "gpt-4o",
        "temperature": 0.5,
    },
    system_message=(
        "You are a helpful AI assistant. "
        "You can answer questions normally, "
        "but if the user requests audio/speech generation, "
        "call the `text_to_speech` tool."
    ),
)

# User Proxy Agent (for testing / API integration)
user_proxy = UserProxyAgent(
    name="user",
    human_input_mode="NEVER",  # API-driven
)
