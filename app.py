import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile
import os

st.set_page_config(page_title="Audio Extractor", layout="centered")
st.title("🎬 Aplikacja do wyodrębniania audio z wideo – v3")

def extract_audio_from_video(video_bytes):
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
            temp_video.write(video_bytes)
            temp_video.flush()
            video_path = temp_video.name

        # Wczytaj wideo i wyciągnij audio
        video_clip = VideoFileClip(video_path)
        audio = video_clip.audio

        # Zapisz audio do pliku tymczasowego
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            audio.write_audiofile(temp_audio.name)
            return temp_audio.name

    except Exception as e:
        st.error(f"Błąd podczas wyodrębniania audio: {e}")
        return None

uploaded_video = st.file_uploader("📤 Prześlij plik wideo (.mp4)", type=["mp4"])

if uploaded_video is not None:
    video_bytes = uploaded_video.read()

    st.video(video_bytes)

    with st.spinner("⏳ Przetwarzanie..."):
        audio_path = extract_audio_from_video(video_bytes)

    if audio_path:
        st.success("✅ Audio zostało wyodrębnione!")
        
        # Odtwarzacz audio
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")

        # Przycisk do pobrania
        st.download_button("⬇️ Pobierz audio (.mp3)", data=audio_bytes, file_name="audio.mp3", mime="audio/mp3")

        # Usuń tymczasowy plik po użyciu
        os.remove(audio_path)
