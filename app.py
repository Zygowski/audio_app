import streamlit as st
import openai
from moviepy.editor import VideoFileClip
import tempfile
import os

st.set_page_config(page_title="Audio Extractor", layout="centered")
st.title("🎧 Aplikacja do podsumowywania audio i wideo – v3")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# Wybór typu pliku
file_option = st.radio("Wybierz typ pliku do przesłania:", ["🎬 Wideo", "🎵 Audio"])

def extract_audio_from_video(video_bytes):
    
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video: # tworzenie tymczasowego pliku wideo
        temp_video.write(video_bytes) # zapisanie przesłanych danych do pliku
        temp_video.flush() # zapewnienie że plik jest zapisany 
        video_path = temp_video.name

    clip = VideoFileClip(video_path)
    audio = clip.audio

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
        audio.write_audiofile(temp_audio.name) # zapisanie audio do tymczasowego pliku
        return temp_audio.name


    
    clip.close()
    return audio_path


def transcribe_audio_file(file_path):
    
        result = openai.Audio.transcribe("whisper-1", open(file_path, "rb"))
        
        return result["text"]


# Uploader dostosowany do wybranego typu
if file_option == "🎬 Wideo":
    uploaded_file = st.file_uploader("Prześlij plik wideo (.mp4)", type=["mp4"])
else:
    uploaded_file = st.file_uploader("Prześlij plik audio (.mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    file_type = uploaded_file.type

    audio_path = None

    with st.spinner("⏳ Przetwarzanie..."):
        if file_option == "🎬 Wideo":
            st.video(file_bytes)
            audio_path = extract_audio_from_video(file_bytes)
        else:
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

                # Transkrypcja audio na tekst
        transcribed_text = transcribe_audio_file(audio_path)
        if transcribed_text:
            st.header("📝 Transkrypcja audio")
            st.text_area("", transcribed_text, height=300)
        
       
        os.remove(audio_path)
