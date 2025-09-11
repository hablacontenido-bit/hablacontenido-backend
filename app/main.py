# app/main.py
from moviepy.editor import VideoFileClip
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from app.schemas import Message
from app.memory import Memory
from app.openai_client import get_response
from pydantic import BaseModel
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import requests, os, uuid, tempfile
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import tempfile, os, uuid, requests
import moviepy.config as mpc
from moviepy.video.tools.drawing import color_split
from app.memory import Memory
from app.agents import assistant, user_proxy

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # origen de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = Memory()

class VideoRequest(BaseModel):
    video_url: str
    quote: str
    author: str

@app.post("/chat/")
async def chat(message: Message):
    try:
        # Agrega el mensaje del usuario al historial
        memory.add_message(message.user_id, "user", message.content)

        # Obtiene el historial de mensajes
        history = memory.get_history(message.user_id)

        # Obtiene la respuesta de OpenAI
        reply = get_response(history)

        # Agrega la respuesta al historial
        memory.add_message(message.user_id, "assistant", reply)

        return {"response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def generate_typing_frames(text, width, font_size=50, padding=20, duration=3, fps=10):
    """Genera una lista de imágenes con efecto máquina de escribir"""
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    frames = []
    total_frames = int(duration * fps)

    # Número de caracteres por frame
    for i in range(1, len(text)+1):
        img = Image.new("RGBA", (width, font_size*3), (0, 0, 0, 160))
        draw = ImageDraw.Draw(img)
        line = text[:i]
        w, _ = draw.textsize(line, font=font)
        draw.text(((width - w) / 2, 10), line, font=font, fill="white")
        frames.append(np.array(img))

    # Repetimos el último frame hasta completar la duración total
    while len(frames) < total_frames:
        frames.append(frames[-1])

    return frames

def create_static_text_image(text, width, font_size=35, padding=20):
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    img = Image.new("RGBA", (width, font_size*3), (0, 0, 0, 160))
    draw = ImageDraw.Draw(img)
    w, _ = draw.textsize(text, font=font)
    draw.text(((width - w) / 2, 10), text, font=font, fill="white")
    return np.array(img)

@app.post("/add_text")
def add_text_to_video(payload: VideoRequest):
    video_url = payload.video_url
    quote = payload.quote
    author = payload.author

    video_id = str(uuid.uuid4())
    temp_dir = tempfile.gettempdir()
    input_path = os.path.join(temp_dir, f"{video_id}_input.mp4")
    output_path = os.path.join(temp_dir, f"{video_id}_output.mp4")

    r = requests.get(video_url)
    if r.status_code != 200:
        raise HTTPException(status_code=400, detail="Unable to download video")
    with open(input_path, "wb") as f:
        f.write(r.content)

    clip = VideoFileClip(input_path)

    try:
        # Texto con efecto máquina de escribir
        typing_frames = generate_typing_frames(quote, clip.w, font_size=50, duration=3, fps=10)
        quote_clip = ImageClip(typing_frames[0]).set_duration(clip.duration)  # default fallback

        from moviepy.editor import ImageSequenceClip
        quote_clip = ImageSequenceClip(typing_frames, fps=10).set_duration(clip.duration).set_position(("center", 50))

        # Autor estático
        author_img = create_static_text_image(f"- {author}", clip.w)
        author_clip = ImageClip(author_img).set_duration(clip.duration).set_position(("center", clip.h - 100))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando overlays: {str(e)}")

    final = CompositeVideoClip([clip, quote_clip, author_clip])
    final.write_videofile(output_path, codec="libx264", audio_codec="aac")

    return {"message": "Success", "video_path": output_path}

@app.get("/download_logs")
def download_logs():
    memory_file = os.path.join(os.path.dirname(__file__), "memory.json")
    if not os.path.exists(memory_file):
        raise HTTPException(status_code=404, detail="No logs found")
    return FileResponse(
        memory_file,
        media_type="application/json",
        filename="memory.json"
    )

@app.post("/agent/")
async def agent_chat(message: Message):
    user_id = message.user_id
    user_message = message.content

    # 1. Load conversation history
    history = memory.get_history(user_id)

    # 2. Add current user message
    memory.add_message(user_id, "user", user_message)

    # 3. Run AutoGen dialogue (stateless by default)
    # We'll inject context by replaying history
    formatted_history = [
        {"role": h["role"], "content": h["content"]} for h in history
    ]
    formatted_history.append({"role": "user", "content": user_message})

    chat_result = user_proxy.initiate_chat(
        assistant,
        message=user_message,
        history=formatted_history  # <— pass memory into AutoGen
    )

    # 4. Save assistant reply
    if isinstance(chat_result, str):
        reply = chat_result
        memory.add_message(user_id, "assistant", reply)
        return {"response": reply, "type": "text"}

    # 5. If tool returns file (audio)
    if isinstance(chat_result, dict) and "file" in chat_result:
        reply = f"Audio generated: {chat_result['file']}"
        memory.add_message(user_id, "assistant", reply)
        return {"response": reply, "type": "audio"}