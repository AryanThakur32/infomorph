#pip install streamlit
#pip install ollama
#pull llama3.1
#pip install edge-tts
#pip install requests
#pip install pillow
#pip install moviepy
#pip install spacy

import random
import base64
import streamlit as st
import streamlit.components.v1 as components
import ollama


import asyncio
import edge_tts  #pip install edge-tts

import requests
import io
from PIL import Image #pip install pillow

#pip install moviepy==1.0.3 numpy>=1.18.1 imageio>=2.5.0 decorator>=4.3.0 tqdm>=4.0.0 Pillow>=7.0.0 scipy>=1.3.0 pydub>=0.23.0 audiofile>=0.0.0 opencv-python>=4.5
from moviepy.editor import AudioFileClip, ImageClip
from moviepy.editor import VideoFileClip, concatenate

import spacy
import spacy.cli
# spacy.cli.download("en_core_web_lg") # lg 500mb md /100 mb /sm 50 mb

# NLP
nlp = spacy.load("en_core_web_sm")

# Hugging Face API
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
HEADERS = {
    "Authorization": "Bearer ur_hugging_face_token",
    "Accept": "image/png"
}

def query(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    if response.status_code == 200 and response.headers['Content-Type'].startswith("image"):
        return response.content
    else:
        print("❌ Error: Returned data doesn't look like an image.")
        print("Response headers:", response.headers)
        print("Response content:", response.text)
        return None

def add_static_image_to_audio(image_path, audio_path, output_path):
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path).set_duration(audio_clip.duration).set_audio(audio_clip)
    image_clip.fps = 1
    image_clip.write_videofile(output_path, codec="libx264")

def merge_videos(video_files, output_file):
    clips = [VideoFileClip(video) for video in video_files]
    final_clip = concatenate(clips, method="compose")
    final_clip.write_videofile(output_file, codec="libx264")

async def sync_main(TEXT, VOICE, rate, pitch_str, file_name):
    communicate = edge_tts.Communicate(TEXT, VOICE, rate=rate, pitch=pitch_str)
    await communicate.save(file_name)

async def get_voices():
    voices = await edge_tts.list_voices()
    return {f"{v['ShortName']} - {v['Locale']} ({v['Gender']})": v['ShortName'] for v in voices}


#background
def set_background(image_file):
    with open(image_file, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/webp;base64,{encoded_string}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Using the .webp image
set_background("background.webp")

st.markdown(
    """
    <style>
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 100%;
        background-color: rgba(0, 0, 0, 0.4);  /* dark overlay */
        z-index: -1;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron&display=swap');

    h1 {
        font-family: 'Orbitron', sans-serif;
        font-size: 60px;
        color: white;
        text-shadow: 2px 2px 8px #000000;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown("<h1></h1>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    input {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white !important;
        padding: 0.75rem;
    }

    button {
        background-color: rgba(0,0,0,0.7) !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load particles.js animation
with open("particles.html", "r") as file:
    particles_background = file.read()

components.html(particles_background, height=40, width=800)




st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")

st.title("INFOMORPH")

#animation text

st.markdown("""
<style>
@keyframes typing {
  from { width: 0 }
  to { width: 100% }
}

.typing-container {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  margin-top: 30px;
}

.typewriter {
  font-family: monospace;
  overflow: hidden;
  white-space: nowrap;
  border-right: 0.15em solid white;
  animation: typing 4s steps(40, end);
  width: 100%;
  max-width: 600px;
  color: white;
  font-size: 1.5rem;
}
</style>

<div class="typing-container">
  <p class="typewriter">Welcome to INFOMORPH — Generating the future...</p>
</div>
""", unsafe_allow_html=True)


topic = st.text_input("Enter Topic:")
create_transcription = st.button("Create Transcription")

if "transcription" not in st.session_state:
    st.session_state["transcription"] = ""

if create_transcription and topic:
    transcription = ollama.generate(
        model='llama3.1',
        prompt=f'You are a skilled storyteller. Write a 5-sentence rich, detailed essay about {topic} covering history, significance, examples, and impact.'
    )
    st.session_state["transcription"] = transcription['response']

transcription = st.session_state["transcription"]
if transcription:
    st.markdown(transcription)
    doc = nlp(transcription)
    sentences = list(doc.sents)

    if st.button("Create Video"):
        video_files = []

        for i, TEXT in enumerate(sentences):
            VOICE = "en-US-AndrewMultilingualNeural"
            rate = "+10%"
            pitch_str = "-10Hz"
            audio_file = f"audio_{i}.mp3"
            asyncio.run(sync_main(TEXT.text, VOICE, rate, pitch_str, audio_file))

            response = ollama.generate(
                model='llama3.1',
                prompt=f"Describe a photorealistic scene for the following: '{TEXT.text}'. Include environment, people, objects, lighting, mood. Output only the visual description."
            )
            image_prompt = response['response']

            image_bytes = query({
                "inputs": image_prompt,
                "parameters": {
                    "width": 1280,
                    "height": 720,
                    "seed": random.randint(1, 999999)
                }
            })

            if image_bytes:
                try:
                    image = Image.open(io.BytesIO(image_bytes))
                    image_path = f"image_{i}.jpeg"
                    image.save(image_path)

                    output_path = f"video_{i}.mp4"
                    add_static_image_to_audio(image_path, audio_file, output_path)
                    video_files.append(output_path)
                    with open(output_path, "rb") as f:
                        st.video(f.read())
                except Exception as e:
                    print(f"❌ Error processing image {i}: {e}")
            else:
                print(f"❌ Failed to generate image for sentence {i}")

        if video_files:
            output_merged = "final_video.mp4"
            merge_videos(video_files, output_merged)
            with open(output_merged, "rb") as f:
                st.video(f.read())

                

