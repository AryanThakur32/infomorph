import streamlit as st
import ollama

#Streamlit app title
st.title("INFOMORPH")

#Input fields for context
topic = st.text_input("Enter Topic:")

if st.button("Create Transcription") or topic:
    transcription = ollama.generate(model='llama3.1',
                               prompt=f'You are a highly skilled storyteller with a knack for weaving intricate narratives. I would like you to write a compelling and in-depth essay about {topic}. The essay should not only explore the fundamental aspects of the topic but also delve into its historical context, significance, and any relevant anecdotes or examples that make it engaging for readers. Please ensure that the writing is rich in detail, thought-provoking, and flows seamlessly from one idea to the next. The final output should be presented as a cohesive block of text without any subtitles or breaks.')

    transcription = transcription['response']
    st.markdown(transcription)

    if st.button("Create Video") and transcription:
        video_titles = ollama.generate(model= 'llama3.1',
                                     prompt = f'Generate 10 compelling and attention-grabbing video titles for the following YouTube video transcription: {transcription}. The titles should be creative, engaging, and designed to spark curiosity among viewers. Use strong action words and phrases that evoke emotion or wonder to attract a broad audience.')
        st.subheader("Video Titles")
        st.markdown(video_titles['response'])

        video_description = ollama.generate(model= 'llama3.1',
                                     prompt = f"Craft a captivating video description for the following YouTube video transcription: {transcription}. The description should include an engaging hook that captures viewers' attention, a brief overview of the video's main topics, and relevant keywords to improve search visibility. Additionally, incorporate a strong call to action encouraging viewers to like, subscribe, and comment on their thoughts or questions. Aim for a tone that reflects the video's content while enticing viewers to watch.")

        st.subheader("Video Description")
        st.markdown(video_description['response'])

        keywords = ollama.generate(model= 'llama3.1',
                                   prompt = f'Please generate 20 highly relevant SEO keywords for optimizing a YouTube video based on the following transcription: {transcription}. Ensure that the keywords capture key themes, concepts, and phrases that viewers might search for related to the content. Focus on a mix of broad and long-tail keywords that reflect both general interest and specific topics discussed in the transcription. The goal is to enhance discoverability and engagement for the video.')
        st.subheader("Keywords")
        st.markdown(keywords['response'])