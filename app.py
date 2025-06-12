import streamlit as st
from moviepy.editor import VideoFileClip
import io
import sys
import subprocess

st.write("Python path:", sys.executable)
try:
    import moviepy.editor
    st.write("moviepy is installed")
except ModuleNotFoundError:
    st.write("moviepy NOT installed")

# Pokaż listę pakietów pip:
installed = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
st.text(installed.stdout)
st.title("Aplikacja do podsumowywania audio i wideo - v3")

file_type = st.radio("Wybierz typ pliku:", ("Audio", "Wideo"))

if file_type == "Audio":
    uploaded_audio = st.file_uploader("Wgraj plik audio", type=["mp3", "wav", "m4a"])
    if uploaded_audio is not None:
        st.audio(uploaded_audio, format="audio/mp3")

elif file_type == "Wideo":
    uploaded_video = st.file_uploader("Wgraj plik wideo", type=["mp4", "mov", "avi", "mkv"])
    if uploaded_video is not None:
        st.video(uploaded_video)
        video_bytes = uploaded_video.read()
        video_buffer = io.BytesIO(video_bytes)

        try:
            clip = VideoFileClip(video_buffer)
            audio_clip = clip.audio

            if audio_clip is not None:
                audio_buffer = io.BytesIO()
                audio_clip.write_audiofile(audio_buffer, codec='mp3', verbose=False, logger=None)
                audio_buffer.seek(0)
                st.audio(audio_buffer, format="audio/mp3")
            else:
                st.warning("To wideo nie zawiera ścieżki audio.")
        except Exception as e:
            st.error(f"Błąd podczas wyodrębniania audio: {e}")
