import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile


st.set_page_config(page_title="Audio Summarizer V2", layout="centered")
st.title("Generetor notatek z audio")

file_type = st.radio("Wybierz typ pliku:", ("Audio", "Wideo"))
if file_type == "Audio":
    uploaded_audio = st.file_uploader("Wybierz plik audio", type=["mp3", "wav", "m4a"])
    
    if uploaded_audio is not None:
        st.success(f"Wczytano plik audio: {uploaded_audio.name}")
        st.audio(uploaded_audio, format="audio/mp3")

elif file_type == "Wideo":
    uploaded_video = st.file_uploader("Wybierz plik wideo", type=["mp4", "mov", "avi", "mkv"])
    
    if uploaded_video is not None:
        st.success(f"Wczytano plik wideo: {uploaded_video.name}")
        st.video(uploaded_video)
                # Ekstrakcja audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(uploaded_video.read())
            temp_video_path = temp_video.name

        video_clip = VideoFileClip(temp_video_path)
        audio_clip = video_clip.audio

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            audio_clip.write_audiofile(temp_audio.name)
            temp_audio.seek(0)
            st.audio(temp_audio.read(), format="audio/mp3")

        audio_clip.close()
        video_clip.close()