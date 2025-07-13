# Import required libraries
import streamlit as st                      # Streamlit for web interface
import requests                             # For API requests
import os                                   # For file paths and env variables
from dotenv import load_dotenv              # To load ElevenLabs API key from .env file

# -----------------  Load API Key -----------------

# Load environment variables from a .env file
load_dotenv()

# Read the ElevenLabs API key from the loaded environment variables
API_KEY = os.getenv("ELEVENLABS_API_KEY")

# If the API key isn't found, show an error and stop execution
if not API_KEY:
    st.error("❌ API key not found. Please check your .env file.")
    st.stop()

# -----------------  Fetch Available Voices from ElevenLabs -----------------

# This function calls the ElevenLabs API and returns a dictionary of voice names and IDs
@st.cache_data(show_spinner=False)
def get_voices():
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": API_KEY}
    response = requests.get(url, headers=headers)
    
    # If request succeeds, extract voices into a dictionary
    if response.status_code == 200:
        voices = response.json()["voices"]
        return {voice["name"]: voice["voice_id"] for voice in voices}
    else:
        st.error(f"❌ Failed to fetch voices: {response.status_code}")
        return {}

# -----------------  Accent Mapping for Voice Filtering -----------------

# Manually tag each voice with its accent for filtering purposes
voice_accents = {
    "Bella": "British",
    "Joseph": "African",
    "Matilda": "African",
    "Fisayo": "Nigerian",   # Custom voices
    "Olabisi": "Nigerian",
    "timi": "Nigerian",
}

# -----------------  Optional Pidgin Converter -----------------

# This function replaces standard English phrases with Nigerian Pidgin alternatives
def stylize_pidgin(text):
    replacements = {
        "you": "yu",
        "I'm": "I dey",
        "I am": "I dey",
        "I'm fine": "I dey kampe",
        "What is happening": "Wetin dey happen",
        "How are you": "How yu dey",
        "going": "dey go",
        "coming": "dey come",
        "are you": "yu dey",
        "already": "don",
        "have you": "yu don",
        "I have": "I don",
        "just": "jus",
        "I will": "I go",
        "I want to": "I wan",
        "do you": "yu dey",
    }
    for eng, pidgin in replacements.items():
        text = text.replace(eng, pidgin)
    return text

# -----------------  ElevenLabs Text-to-Speech API Call -----------------

# Sends text to ElevenLabs and saves the returned audio file locally
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

    # Send POST request and handle response
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    else:
        st.error(f"❌ Error: {response.status_code} - {response.text}")
        return None

# -----------------  Streamlit Web App UI -----------------

# Page Title
st.title("🗣️ ElevenLabs TTS App with Nigerian Pidgin & Accent Filter")

# Step 1: Fetch voices from ElevenLabs
voice_map = get_voices()

# Step 2: Define and insert your custom Nigerian voices
custom_voices = {
    "Fisayo": "it5NMxoQQ2INIh4XcO44",
    "Olabisi": "eOHsvebhdtt0XFeHVMQY",
    "timi": "yp4MmTRKvE7VXY3hUJRY"
}

# Step 3: Avoid duplication by removing any built-in voices with the same names
for name in custom_voices:
    voice_map.pop(name, None)  # Remove if already exists from ElevenLabs API

# Step 4: Merge custom voices into the voice map
voice_map.update(custom_voices)

# Step 5: Add them to the accent filter mapping
voice_accents.update({
    "Fisayo": "Nigerian",
    "Olabisi": "Nigerian",
    "timi": "Nigerian"
})

# Step 6: If no voices are available, stop the app
if not voice_map:
    st.stop()

# Step 7: Create dropdown for accent filtering
accent_options = ["All", "Nigerian", "African", "American", "British"]
selected_accent = st.selectbox("🌐 Filter voices by accent:", accent_options)

# Step 8: Filter voices based on the selected accent
if selected_accent == "All":
    filtered_voices = voice_map
else:
    filtered_voices = {
        name: vid for name, vid in voice_map.items()
        if voice_accents.get(name, "Unknown") == selected_accent
    }

# Step 9: If no matching voices found, show warning
if not filtered_voices:
    st.warning("No voices found for selected accent.")
    st.stop()

# Step 10: Allow user to select a voice from the filtered list
voice_names = sorted(filtered_voices.keys())
selected_voice = st.selectbox("🎤 Choose a voice:", voice_names, index=0)
selected_voice_id = filtered_voices[selected_voice]

# Step 11: Show preview audio if available
preview_url = f"https://api.elevenlabs.io/v1/voices/{selected_voice_id}"
headers = {"xi-api-key": API_KEY}
res = requests.get(preview_url, headers=headers)
if res.status_code == 200 and "preview_url" in res.json():
    st.audio(res.json()["preview_url"], format="audio/mp3")

# Step 12: Get user input text
text_input = st.text_area("Type your text here:", height=150)

# Step 13: Toggle for Pidgin auto-style
pidgin_mode = st.checkbox("🗣️ Auto-style for Nigerian Pidgin")
if pidgin_mode:
    st.markdown("💡 *Your text will be stylized for Nigerian Pidgin pronunciation.*")

# Step 14: Generate button to create audio
if st.button("🔊 Generate Audio"):
    if not text_input.strip():
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("🔄 Generating audio..."):
            # Convert to Pidgin if checkbox is enabled
            final_text = stylize_pidgin(text_input) if pidgin_mode else text_input
            
            # Call ElevenLabs API to generate audio
            audio_file = text_to_speech(final_text, selected_voice_id)
            
            # If successful, play and offer download
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
