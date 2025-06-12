import streamlit as st
import ffmpeg

st.set_page_config(page_title="Audio/Video Summarizer V3", layout="centered")
st.title("📼 Wgraj plik audio lub wideo")

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

        in_memory_video = uploaded_video.read()

        try:
            out, err = ffmpeg.run(
                ffmpeg.input('pipe:0')
                      .output('pipe:1', format='mp3', acodec='mp3'),
                input=in_memory_video,
                capture_stdout=True,
                capture_stderr=True
            )
            st.audio(out, format='audio/mp3')
        except ffmpeg.Error as e:
            st.error(f"Błąd ffmpeg: {e.stderr.decode()}")
