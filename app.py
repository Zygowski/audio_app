import streamlit as st
import openai
from moviepy.editor import VideoFileClip
import tempfile
import os
import yt_dlp


st.set_page_config(page_title="Audio Extractor", layout="centered")
st.title("🎧 Generator podsumowań wideo i audio 🎧")


if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False
if "api_key" not in st.session_state:
    st.session_state.api_key = None

# Spróbuj pobrać klucz z secrets
api_key_from_secrets = None
try:
    api_key_from_secrets = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

if api_key_from_secrets:
    openai.api_key = api_key_from_secrets
    st.session_state.api_key = api_key_from_secrets
    st.session_state.api_key_valid = True

if not st.session_state.api_key_valid:
     with st.sidebar:
        st.markdown("### 🔐 Klucz OpenAI API")
        user_key = st.text_input("Wprowadź swój OpenAI API Key:", type="password", key="input_api_key")
    
    
        if user_key:
            try:
                openai.api_key = user_key
                openai.Engine.list()  # Test poprawności klucza
            except Exception:
                st.error("❌ Nieprawidłowy klucz API.")
                st.stop()  # Zatrzymaj dalsze wykonanie
            else:
                # Jeśli test przeszedł OK
                st.session_state.api_key = user_key
                st.session_state.api_key_valid = True
                st.success("✅ Klucz poprawny.")
                st.rerun()  # Przeładuj aplikację, żeby ukryć input
else:
    openai.api_key = st.session_state.api_key



# Wybór typu pliku
source_option = st.radio("Wybierz źródło:", ["📂 Plik lokalny", "🌐 YouTube"])
file_option = st.radio("Wybierz typ pliku:", ["🎬 Wideo", "🎵 Audio"])

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


def download_audio_from_youtube(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'cookiefile': 'cookies.txt',  # Upewnij się, że masz ten plik w katalogu
        'quiet': False,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return 'downloaded_audio.mp3'


def split_text(text, max_chars=3000):
    chunks = []
    while len(text) > max_chars:
        split_index = text.rfind('.', 0, max_chars) # szukanie ostaniej kropki żeby ładnie podzielić tekst 
        if split_index == -1:
            split_index = max_chars # jak nie ma kropki to kroji w miejscie max_chars
        chunks.append(text[:split_index + 1].strip()) # wycinamy tekst +1 czyli kropka 
        text = text[split_index + 1:].strip() # skracamy cały tekst o to co juz zostało przetworzone
    chunks.append(text) # gdy jest juz podzielone dodajemy reszte tekstu jako ostatni fragment
    return chunks

def summarize_text(text):
    chunks = split_text(text)
    summaries = []

    for i, chunk in enumerate(chunks):
        prompt = (
            "Przekształć poniższą transkrypcję na zwięzłe, klarowne notatki punktowane:\n\n"
            f"{chunk}\n\n"
            "Notatki:"
        )
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Jesteś pomocnym asystentem."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
        )
        summaries.append(response.choices[0].message["content"].strip())

    return "\n\n".join(summaries)
uploaded_file = None
youtube_url = None

# Uploader dostosowany do wybranego typu
if source_option == "📂 Plik lokalny":
    if file_option == "🎬 Wideo":
        uploaded_file = st.file_uploader("Prześlij plik wideo (.mp4)", type=["mp4"])
    else:
        uploaded_file = st.file_uploader("Prześlij plik audio (.mp3, .wav, .m4a)", type=["mp3", "wav", "m4a"])
else:
    youtube_url = st.text_input("Wklej link do filmu na YouTube:")

if uploaded_file is not None or (youtube_url and source_option == "🌐 YouTube"):
    with st.spinner("⏳ Przetwarzanie..."):
        audio_path = None

        if source_option == "📂 Plik lokalny":
            file_bytes = uploaded_file.read()
            if file_option == "🎬 Wideo":
                st.video(file_bytes)
                audio_path = extract_audio_from_video(file_bytes)
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                    temp_audio.write(file_bytes)
                    temp_audio.flush()
                    audio_path = temp_audio.name
                st.audio(file_bytes, format=uploaded_file.type)
        else:
            st.info("⏬ Pobieranie audio z YouTube...")
            audio_path = download_audio_from_youtube(youtube_url)
            st.audio(audio_path)

        transcription = transcribe_audio(audio_path)
        #st.markdown("### 🗒️ Transkrypcja:")
        #st.write(transcription)

        summary = summarize_text(transcription)
        st.markdown("### 📝 Notatka:")
        st.write(summary)

        os.remove(audio_path)