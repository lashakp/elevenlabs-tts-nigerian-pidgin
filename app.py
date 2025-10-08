# app.py
import streamlit as st
import os
import base64
import logging
from dotenv import load_dotenv
from utils.api import get_voices, text_to_speech, get_voice_preview, validate_api_key
from utils.pidgin import stylize_pidgin
from utils.constants import VOICE_ACCENTS, REPLACEMENTS

logging.basicConfig(filename="tts_app.log", level=logging.ERROR)

load_dotenv()
API_KEY = st.secrets.get("ELEVENLABS_API_KEY") or os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    st.error("❌ API key not found. Add to Streamlit secrets or .env file.")
    st.stop()
if not validate_api_key(API_KEY):
    st.error("❌ Invalid ElevenLabs API key.")
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []
if "generation_count" not in st.session_state:
    st.session_state.generation_count = 0

st.title("🗣️ ElevenLabs TTS App with Nigerian Pidgin & Accent Filter")
st.markdown("Enter text to convert to speech. Enable **Pidgin Mode** to automatically translate English to Nigerian Pidgin.")

# Dialect Selection (Stub)
dialect = st.selectbox("Dialect", ["Nigerian Pidgin", "Other (Coming Soon)"])
if dialect != "Nigerian Pidgin":
    st.info("Other dialects not yet implemented.")

# Voice Selection
with st.container():
    st.markdown("### 🎤 Voice Selection")
    accent_options = ["All", "Nigerian", "African", "American", "British"]
    selected_accent = st.selectbox("🌐 Filter voices by accent:", accent_options)
    voice_map = get_voices(API_KEY)

    custom_voices = {
        "Fisayo": "it5NMxoQQ2INIh4XcO44",
        "Olabisi": "eOHsvebhdtt0XFeHVMQY",
        "timi": "yp4MmTRKvE7VXY3hUJRY"
    }
    for name in custom_voices:
        voice_map.pop(name, None)
    voice_map.update(custom_voices)
    VOICE_ACCENTS.update({
        "Fisayo": "Nigerian",
        "Olabisi": "Nigerian",
        "timi": "Nigerian"
    })

    filtered_voices = (
        voice_map if selected_accent == "All" else {
            name: vid for name, vid in voice_map.items()
            if VOICE_ACCENTS.get(name, "Unknown") == selected_accent
        }
    )
    if not filtered_voices:
        st.warning("No voices found for selected accent.")
        st.stop()

    voice_names = sorted(filtered_voices.keys())
    selected_voice = st.selectbox("🎤 Choose a voice:", voice_names, index=0)
    selected_voice_id = filtered_voices[selected_voice]

    preview_url = get_voice_preview(selected_voice_id, API_KEY)
    if preview_url:
        st.audio(preview_url, format="audio/mp3")

# Advanced Settings
with st.expander("🔧 Advanced Voice Settings"):
    stability = st.slider("Stability", 0.0, 1.0, 0.75, 0.05)
    similarity_boost = st.slider("Similarity Boost", 0.0, 1.0, 0.75, 0.05)

# Text Input
st.markdown("## 📝 Enter Your Text")
uploaded_file = st.file_uploader("Upload a text file for batch TTS", type=["txt"])
text_input = ""
if uploaded_file:
    text_input = uploaded_file.read().decode("utf-8")
    st.text_area("Uploaded Text:", text_input, height=150, disabled=True)
else:
    text_input = st.text_area("Type your text here:", height=150)

MAX_TEXT_LENGTH = 5000
if len(text_input) > MAX_TEXT_LENGTH:
    st.error(f"⚠️ Text exceeds {MAX_TEXT_LENGTH} characters. Please shorten it.")
    st.stop()

# Pidgin Controls
col1, col2 = st.columns(2)
with col1:
    pidgin_mode = st.checkbox("🗣️ Auto-style for Nigerian Pidgin", value=False)
with col2:
    show_changes = st.checkbox("👁️ Show English ➝ Pidgin replacements", value=False)

# Custom Replacements
st.markdown("### 🛠️ Custom Pidgin Replacements")
custom_replacements_input = st.text_area("Add custom English → Pidgin replacements (one per line, format: English|Pidgin)", height=100)
custom_replacements = []
if custom_replacements_input:
    for line in custom_replacements_input.split("\n"):
        if "|" in line:
            eng, pidgin = line.split("|", 1)
            custom_replacements.append((eng.strip().lower(), pidgin.strip()))

# Stylize Text
if pidgin_mode and text_input.strip():
    stylized_text = stylize_pidgin(text_input, custom_replacements)
    if show_changes:
        st.markdown("### 🔤 English ➝ Pidgin Replacements")
        all_reps = REPLACEMENTS + custom_replacements
        changes = [f"- `{eng}` ➝ `{pidgin}`" for eng, pidgin in all_reps if eng.lower() in text_input.lower()]
        if changes:
            st.markdown("\n".join(changes))
        else:
            st.info("ℹ️ No substitutions found.")
    st.markdown("### 🗣️ Stylized Pidgin Text")
    st.code(stylized_text, language="text")
else:
    stylized_text = text_input

# Generate Audio
st.markdown("## 🔊 Generate Audio")
if st.button("🎙️ Generate Audio"):
    if not text_input.strip():
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("🔄 Generating audio..."):
            try:
                audio_file = text_to_speech(stylized_text, selected_voice_id, API_KEY, 
                                            stability=stability, similarity_boost=similarity_boost)
                if audio_file:
                    st.audio(audio_file, format="audio/mp3")
                    playback_speed = st.selectbox("Playback Speed", [0.5, 1.0, 1.5, 2.0], index=1)
                    audio_data = base64.b64encode(open(audio_file, "rb").read()).decode()
                    st.markdown(f'<audio controls playbackRate="{playback_speed}"><source src="data:audio/mp3;base64,{audio_data}" type="audio/mp3"></audio>', unsafe_allow_html=True)
                    
                    with open(audio_file, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Audio",
                            data=f,
                            file_name="tts_output.mp3",
                            mime="audio/mpeg"
                        )
                    st.session_state.history.append({"text": stylized_text, "voice": selected_voice, "file": audio_file})
                    st.session_state.generation_count += 1
                    st.success("✅ Audio generated successfully!")
                    st.info(f"Total generations: {st.session_state.generation_count}")
            except Exception as e:
                logging.error(f"Generation Error: {str(e)}")
                st.error(f"❌ An unexpected error occurred: {str(e)}. Check tts_app.log.")

# History
with st.expander("📜 History"):
    for idx, entry in enumerate(st.session_state.history):
        st.write(f"Entry {idx+1}: Text: {entry['text']} | Voice: {entry['voice']}")
        st.audio(entry["file"], format="audio/mp3")
