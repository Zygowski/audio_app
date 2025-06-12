import streamlit as st

st.set_page_config(page_title="Audio Summarizer V1", layout="centered")
st.title("🎧 Wgraj plik audio")

uploaded_file = st.file_uploader("Wybierz plik audio", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    st.success(f"Wczytano plik: {uploaded_file.name}")

    # Odtwarzanie audio bez zapisu
    st.audio(uploaded_file, format="audio/mp3")