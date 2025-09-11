# app/agents.py
from autogen import AssistantAgent, UserProxyAgent, register_function
from app.tools.elevenlabs_tool import text_to_speech_tool

# Create agents first
assistant = AssistantAgent(
    name="assistant",
    llm_config={
        "model": "gpt-4o-mini",
        "temperature": 0.5,
    },
    system_message=(
        "You are a helpful AI assistant. "
        "Answer questions normally, but if the user requests audio/speech, "
        "call the `text_to_speech` tool."
    ),
)

user_proxy = UserProxyAgent(
    name="user",
    human_input_mode="NEVER",  # API-driven
    code_execution_config={"use_docker": False},
)

# Register ElevenLabs tool — new API requires caller + executor
register_function(
    text_to_speech_tool,
    name="text_to_speech",
    description="Generate speech from text using ElevenLabs API",
    caller=assistant,   # who can call the tool
    executor=user_proxy # who executes the function
)
