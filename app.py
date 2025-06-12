import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile
import os

st.set_page_config(page_title="Audio Extractor", layout="centered")
st.title("🎧 Aplikacja do podsumowywania audio i wideo – v3")

def extract_audio_from_video(video_bytes):
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
            temp_video.write(video_bytes)
            temp_video.flush()
            video_path = temp_video.name

        video_clip = VideoFileClip(video_path)
        audio = video_clip.audio

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            audio.write_audiofile(temp_audio.name)
            return temp_audio.name

    except Exception as e:
        st.error(f"Błąd podczas wyodrębniania audio: {e}")
        return None

uploaded_file = st.file_uploader("📤 Prześlij plik wideo (.mp4) lub audio (.mp3/.wav/.m4a)", type=["mp4", "mp3", "wav", "m4a"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_type = uploaded_file.type

    audio_path = None

    with st.spinner("⏳ Przetwarzanie..."):
        if file_type == "video/mp4":
            st.video(file_bytes)
            audio_path = extract_audio_from_video(file_bytes)

        elif file_type in ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4"]:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_audio.write(file_bytes)
                temp_audio.flush()
                audio_path = temp_audio.name

    if audio_path:
        st.success("✅ Audio gotowe!")

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button("⬇️ Pobierz audio (.mp3)", data=audio_bytes, file_name="audio.mp3", mime="audio/mp3")

        os.remove(audio_path)
