import streamlit as st
import openai
from moviepy.editor import VideoFileClip
import tempfile
import os

st.set_page_config(page_title="Audio Extractor", layout="centered")
st.title("🎧 Generator podsumowań wideo i audio 🎧")

# Obsługa klucza OpenAI API – z `st.secrets` lub ręcznego wpisania
# Obsługa klucza API – z secrets lub ręcznego wpisania
if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.markdown("🔐 Nie znaleziono klucza API OpenAI.")
    st.markdown("Aby korzystać z tej aplikacji, wprowadź swój klucz API poniżej.")
    user_key = st.text_input("Wprowadź swój OpenAI API Key:", type="password")
    if user_key:
        openai.api_key = user_key
    else:
        st.stop()


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
    os.remove(video_path)  # Usunięcie tymczasowego pliku wideo
    return audio_path


def transcribe_audio(file_path):
     
    audio_file = open(file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

def summarize_text(text):
    prompt = (
        "Przekształć poniższą transkrypcję na zwięzłe, klarowne notatki punktowane:\n\n"
        f"{text}\n\n"
        "Notatki:"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Jesteś pomocnym asystentem."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=300,
    )
    return response.choices[0].message['content'].strip()

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
            # Odtwarzanie wyodrębnionego dźwięku
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")
        
        transcription = transcribe_audio(audio_path)
        st.markdown("### 🗒️ Transkrypcja:")
        st.write(transcription)

        summary = summarize_text(transcription)
        st.markdown("### 📝 Notatka:")
        st.write(summary)
        
        os.remove(audio_path)
