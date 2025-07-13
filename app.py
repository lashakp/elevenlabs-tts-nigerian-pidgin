# Import required libraries
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# -----------------  Load API Key -----------------

load_dotenv()
API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not API_KEY:
    st.error("❌ API key not found. Please check your .env file.")
    st.stop()

# -----------------  Fetch Available Voices -----------------

@st.cache_data(show_spinner=False)
def get_voices():
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices = response.json()["voices"]
        return {voice["name"]: voice["voice_id"] for voice in voices}
    else:
        st.error(f"❌ Failed to fetch voices: {response.status_code}")
        return {}

# -----------------  Accent Mapping -----------------

voice_accents = {
    "Bella": "British",
    "Joseph": "African",
    "Matilda": "African",
    "Fisayo": "Nigerian",
    "Olabisi": "Nigerian",
    "timi": "Nigerian",
}

# -----------------  Pidgin Converter -----------------

replacements = {
    "you": "yu", "your": "yu", "are": "dey", "I'm": "I dey", "she will": "she go", 
    "he will": "him go", "it will": "e go", "they will": "dem go", 
    "I will":"i go", "We will": "We go", "she is": "she dey", "it is": "e dey",
    "they are": "dem dey", "he is": "him dey", "I have": "I don",
    "I had": "I don get", "I can": "I fit", "I could": "I fit",
    "I should": "I suppose", "I would": "I go", "I might": "I fit",
    "I may": "I fit", "I must": "I gatz", "I don't": "I no",
    "I do not": "I no", "I cannot": "I no fit", "I can't": "I no fit",
    "I cannot do": "I no fit do", "I cannot go": "I no fit go",
    "I cannot come": "I no fit come", "I cannot see": "I no fit see",
    "I cannot hear": "I no fit hear", "I cannot understand": "I no fit understand",
    "I cannot speak": "I no fit talk", "I cannot eat": "I no fit chop",
    "I want": "I wan", "We are": "We dey", "We have": "We don",
    "We want": "We wan", "I need": "I need", "I'm fine": "I dey kampe",
    "What is happening": "Wetin dey happen", "How are you": "How yu dey",
    "going": "dey go", "coming": "dey come", "are you": "yu dey",
    "already": "don", "have you": "yu don", "just": "jus",
    "I want to": "I wan", "do you": "yu dey"
}

def stylize_pidgin(text):
    for eng, pidgin in replacements.items():
        text = text.replace(eng, pidgin)
    return text

# -----------------  ElevenLabs API Call -----------------

def text_to_speech(text, voice_id, output_path="output.mp3"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    else:
        st.error(f"❌ Error: {response.status_code} - {response.text}")
        return None

# -----------------  Streamlit UI -----------------

st.title("🗣️ ElevenLabs TTS App with Nigerian Pidgin & Accent Filter")

# Step 1: Fetch voices
voice_map = get_voices()

# Step 2: Add custom voices
custom_voices = {
    "Fisayo": "it5NMxoQQ2INIh4XcO44",
    "Olabisi": "eOHsvebhdtt0XFeHVMQY",
    "timi": "yp4MmTRKvE7VXY3hUJRY"
}
for name in custom_voices:
    voice_map.pop(name, None)
voice_map.update(custom_voices)
voice_accents.update({
    "Fisayo": "Nigerian",
    "Olabisi": "Nigerian",
    "timi": "Nigerian"
})

if not voice_map:
    st.stop()

# Step 3: Accent Filter
accent_options = ["All", "Nigerian", "African", "American", "British"]
selected_accent = st.selectbox("🌐 Filter voices by accent:", accent_options)
filtered_voices = (
    voice_map if selected_accent == "All" else {
        name: vid for name, vid in voice_map.items()
        if voice_accents.get(name, "Unknown") == selected_accent
    }
)
if not filtered_voices:
    st.warning("No voices found for selected accent.")
    st.stop()

# Step 4: Voice Selection
voice_names = sorted(filtered_voices.keys())
selected_voice = st.selectbox("🎤 Choose a voice:", voice_names, index=0)
selected_voice_id = filtered_voices[selected_voice]

# Step 5: Preview
preview_url = f"https://api.elevenlabs.io/v1/voices/{selected_voice_id}"
headers = {"xi-api-key": API_KEY}
res = requests.get(preview_url, headers=headers)
if res.status_code == 200 and "preview_url" in res.json():
    st.audio(res.json()["preview_url"], format="audio/mp3")

# -----------------  User Input and Controls -----------------

st.markdown("## 📝 Enter Your Text")

text_input = st.text_area("Type your text here:", height=150, key="input_text_area")

col1, col2 = st.columns(2)
with col1:
    pidgin_mode = st.checkbox("🗣️ Auto-style for Nigerian Pidgin", value=False)
with col2:
    show_changes = st.checkbox("👁️ Show English ➝ Pidgin replacements", value=False)

if pidgin_mode and text_input.strip():
    stylized_text = stylize_pidgin(text_input)

    if show_changes:
        st.markdown("### 🔤 English ➝ Pidgin Replacements")
        changes = []
        for eng, pidgin in replacements.items():
            if eng in text_input:
                changes.append(f"- `{eng}` ➝ `{pidgin}`")
        if changes:
            st.markdown("\n".join(changes))
        else:
            st.info("ℹ️ No substitutions found.")

    st.markdown("### 🗣️ Stylized Pidgin Text")
    st.code(stylized_text, language="text")
else:
    stylized_text = text_input

# -----------------  Generate Audio -----------------

st.markdown("## 🔊 Generate Audio")

if st.button("🎙️ Generate Audio"):
    if not text_input.strip():
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("🔄 Generating audio..."):
            audio_file = text_to_speech(stylized_text, selected_voice_id)
            if audio_file:
                st.audio(audio_file, format="audio/mp3")
                with open(audio_file, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Audio",
                        data=f,
                        file_name="tts_output.mp3",
                        mime="audio/mpeg"
                    )
                st.success("✅ Audio generated successfully!")
