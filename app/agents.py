# app/agents.py
from autogen import AssistantAgent, UserProxyAgent, register_function
from app.tools.elevenlabs_tool import text_to_speech_tool

def load_prompt(filename: str) -> str:
    """Reads a prompt text file from the prompts/ folder."""
    base_dir = os.path.dirname(__file__)  # directory of current script
    file_path = os.path.join(base_dir, "prompts", filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

instruction = load_prompt("instruction.txt")
context = load_prompt("context.txt")

# Create agents first
assistant = AssistantAgent(
    name="assistant",
    llm_config={
        "model": "gpt-4o",
        "temperature": 0.5,
    },
    system_message=(instruction + "\n\n" + context),
)

user_proxy = UserProxyAgent(
    name="user",
    human_input_mode="NEVER",  # API-driven
    code_execution_config={"use_docker": False},
    default_auto_reply="TERMINATE" 
)

# Register ElevenLabs tool — new API requires caller + executor
register_function(
    text_to_speech_tool,
    name="text_to_speech",
    description="Generate speech from text using ElevenLabs API",
    caller=assistant,   # who can call the tool
    executor=user_proxy # who executes the function
)
