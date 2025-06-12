import streamlit as st

st.set_page_config(page_title="Audio Summarizer V2", layout="centered")
st.title("Generetor notatek z audio")

uploaded_file = st.file_uploader("Wybierz plik audio", type=["mp3", "wav", "m4a"])
uploaded_file = st.file_uploader("Wybierz plik wideo", type=["mp4", "mov", "avi", "mkv"])
if uploaded_file is not None:
    st.success(f"Wczytano plik: {uploaded_file.name}")

    # Odtwarzanie audio bez zapisu
    st.audio(uploaded_file, format="audio/mp3")
    st.video(uploaded_file)