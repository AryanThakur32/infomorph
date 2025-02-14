import streamlit as st
import ollama

import asyncio
import edge_tts  #pip install edge-tts

import requests
import io
from PIL import Image #pip install pillow

from moviepy.editor import AudioFileClip, ImageClip
from moviepy.editor import VideoFileClip, concatenate_videoclips

import spacy
import spacy.cli
# spacy.cli.download("en_core_web_lg") # lg 500mb md /100 mb /sm 50 mb


nlp = spacy.load("en_core_web_lg")

API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
headers = {"Authorization": "Bearer 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"}

def merge_videos(video_files, output_file):
    """Merge multiple video files into a single video file."""
    clips = [VideoFileClip(video) for video in video_files]
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(output_file, codec="libx264")


def add_static_image_to_audio(image_path, audio_path, output_path):
    """Create and save a video file by combining a static image with an audio file."""

    # Create the audio clip object
    audio_clip = AudioFileClip(audio_path)

    # Create the image clip object
    image_clip = ImageClip(image_path)

    # Use set_audio method from image clip to combine the audio with the image
    video_clip = image_clip.set_audio(audio_clip)

    # Specify the duration of the new clip to be the duration of the audio clip
    video_clip.duration = audio_clip.duration

    # Set the FPS to 1 (you can adjust this if needed)
    video_clip.fps = 1

    # Write the resulting video clip to a file
    video_clip.write_videofile(output_path)

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content


async def sync_main(TEXT, VOICE, rate, pitch_str, file_name) -> None:
    """Main function"""
    communicate = edge_tts.Communicate(TEXT, VOICE, rate=rate, pitch=pitch_str)
    await communicate.save(file_name)  # Use the asynchronous save method

# Get all available voices
async def get_voices():
    voices = await edge_tts.list_voices()
    return {f"{v['ShortName']} - {v['Locale']} ({v['Gender']})": v['ShortName'] for v in voices}

# Streamlit app title
st.title("Video Creator")

# Input fields for context
topic = st.text_input("Enter Topic:")

create_transcription = st.button("Create Transcription")

if "transcription" not in st.session_state:
    st.session_state["transcription"] = ""
if create_transcription or topic:

    voices = asyncio.run(get_voices())
    # print(voices.keys())
    # st.write(voices)
    # st.write(len(voices))

   # Ensure session state variable is initialized


if create_transcription:
    transcription = ollama.generate(
        model='llama3.1',
        prompt=f'You are a highly skilled storyteller with a knack for weaving intricate narratives. I would like you to write a compelling and in-depth essay about {topic}. The essay should not only explore the fundamental aspects of the topic but also delve into its historical context, significance, and any relevant anecdotes or examples that make it engaging for readers. Please ensure that the writing is rich in detail, thought-provoking, and flows seamlessly from one idea to the next. The final output should be presented as a cohesive block of text without any subtitles or breaks.But keep in mind to not use more than 5 sentences.'
    )

    # Extract the response from the Ollama output
    transcription = transcription['response']

    # Store transcription in session state
    st.session_state["transcription"] = transcription

# Retrieve transcription safely
transcription = st.session_state["transcription"]

# Display transcription
st.markdown(transcription)

# Process the transcription with NLP
nlp = spacy.load("en_core_web_sm")
doc = nlp(transcription)

    # Split the text into sentences

sentences = list(doc.sents)
st.markdown(len(sentences))

if st.button("Create Video") and transcription:
        video_titles = ollama.generate(model='llama3.1',
                                       prompt=f'Generate 10 compelling and attention-grabbing video titles for the following YouTube video transcription: {transcription}. The titles should be creative, engaging, and designed to spark curiosity among viewers. Use strong action words and phrases that evoke emotion or wonder to attract a broad audience.')
        st.subheader("Video Titles")
        st.markdown(video_titles['response'])

        video_description = ollama.generate(model='llama3.1',
                                            prompt=f"Craft a captivating video description for the following YouTube video transcription: {transcription}. The description should include an engaging hook that captures viewers' attention, a brief overview of the video's main topics, and relevant keywords to improve search visibility. Additionally, incorporate a strong call to action encouraging viewers to like, subscribe, and comment on their thoughts or questions. Aim for a tone that reflects the video's content while enticing viewers to watch.")

        st.subheader("Video Description")
        st.markdown(video_description['response'])

        keywords = ollama.generate(model='llama3.1',
                                   prompt=f'Please generate 20 highly relevant SEO keywords for optimizing a YouTube video based on the following transcription: {transcription}. Ensure that the keywords capture key themes, concepts, and phrases that viewers might search for related to the content. Focus on a mix of broad and long-tail keywords that reflect both general interest and specific topics discussed in the transcription. The goal is to enhance discoverability and engagement for the video.')
        st.subheader("Keywords")
        st.markdown(keywords['response'])


        video_files = []
        for i, TEXT in enumerate(sentences):
            VOICE = "en-US-AndrewMultilingualNeural"
            rate = "+10%" # -20 - +20
            pitch_str = "-10Hz"
            file_name = f"test{i}.mp3"
            # Use asyncio.run to execute the async function
            asyncio.run(sync_main(TEXT.text, VOICE, rate, pitch_str, file_name))
            st.audio(file_name, format="audio/mp3")
            st.markdown(TEXT.text)

            response = ollama.generate(
                model='llama3.1',
                prompt=f"Create a detailed prompt for a text-to-image model to create ultra-realistic image based on the following paragraph: '{TEXT.text}'. The prompt should include descriptions of the scene. Output only include prompt, do not add any other explanation like: Here is the detailed prompt for a text-to-image model."
            )  # , the character's appearance, and the mood of the setting
            print(response['response'])

            # Set the API URL and headers

            # Query the API with the user's input
            image_bytes = query({"inputs": response['response'],
                                 "parameters":
                                     {"width": 1280,
                                      "height": 720}})  # x8 16/9

            # Open the image using PIL
            # print(image_bytes)
            image = Image.open(io.BytesIO(image_bytes))
            image.save(f"image{i}.jpeg")
            # Display the generated image
            st.image(image, caption=f"Generated Image for: '{response['response']}'", use_column_width=True)


            image_path = f"image{i}.jpeg"  # Change this to your JPEG file path
            audio_path = f"test{i}.mp3"  # Change this to your MP3 file path
            output_path = f"output_video{i}.mp4"  # Change this to your desired output video file path

            add_static_image_to_audio(image_path, audio_path, output_path)
            video_files.append(output_path)

            with open(output_path, "rb") as video_file:
                video_bytes = video_file.read()
            # Display the video
            st.video(video_bytes, format="video/mp4")

        output_file = "merged_video.mp4"
        merge_videos(video_files, output_file)

        # Open the video file in binary mode
        with open("merged_video.mp4", "rb") as video_file:
            merge_video_bytes = video_file.read()

        # Display the video
        st.video(merge_video_bytes, format="video/mp4")