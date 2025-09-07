# -----------------  Import required libraries -----------------
import streamlit as st        # Streamlit → build the web app UI
import requests               # Requests → send HTTP requests to ElevenLabs API
import os                     # OS → access environment variables (like API key)
from dotenv import load_dotenv # dotenv → load secrets from a .env file


# -----------------  Load API Key -----------------

load_dotenv()  # Load environment variables from .env file (if exists)
API_KEY = os.getenv("ELEVENLABS_API_KEY")  # Fetch the ElevenLabs API key

# If API key not found → stop execution
if not API_KEY:
    st.error("❌ API key not found. Please check your .env file.")
    st.stop()


# -----------------  Fetch Available Voices -----------------

@st.cache_data(show_spinner=False)  # Cache response to avoid repeated API calls
def get_voices():
    url = "https://api.elevenlabs.io/v1/voices"  # Endpoint to fetch voices
    headers = {"xi-api-key": API_KEY}            # Pass API key in header
    response = requests.get(url, headers=headers)  # Send GET request
    if response.status_code == 200:  # ✅ Success
        voices = response.json()["voices"]       # Extract voices from JSON
        # Return dict: {"VoiceName": "VoiceID"}
        return {voice["name"]: voice["voice_id"] for voice in voices}
    else:  # ❌ Error
        st.error(f"❌ Failed to fetch voices: {response.status_code}")
        return {}


# -----------------  Accent Mapping -----------------

# Manually assign accents to certain voices
voice_accents = {
    "Bella": "British",
    "Joseph": "African",
    "Matilda": "African",
    "Fisayo": "Nigerian",
    "Olabisi": "Nigerian",
    "timi": "Nigerian",
}


# -----------------  Pidgin Converter -----------------

# Dictionary of English → Nigerian Pidgin replacements
Replacements = [
    ("i cannot understand", "i no fit understand"),
    ("i cannot speak", "i no fit talk"),
    ("i cannot come", "i no fit come"),
    ("i cannot do", "i no fit do"),
    ("i cannot eat", "i no fit chop"),
    ("i cannot go", "i no fit go"),
    ("i cannot hear", "i no fit hear"),
    ("i cannot see", "i no fit see"),
    ("i cannot", "i no fit"),
    ("i can't", "i no fit"),
    ("i do not want", "i no wan"),
    ("i do not have", "i no get"),
    ("i do not", "i no"),
    ("i don't", "i no"),
    ("what is happening", "wetin dey happen"),
    ("how are you", "how yu dey"),
    ("i'm fine", "i dey kampe"),
    ("are you", "yu dey"),
    ("have you", "yu don"),
    ("do you", "yu dey"),
    ("i want to", "i wan"),
    ("i should", "i suppose"),
    ("i would", "i go"),
    ("i might", "i fit"),
    ("i may", "i fit"),
    ("i must", "i gatz"),
    ("i want", "i wan"),
    ("i need", "i need"),
    ("she will", "she go"),
    ("he will", "him go"),
    ("it will", "e go"),
    ("they will", "dem go"),
    ("we will", "we go"),
    ("i will", "i go"),
    ("she is", "she dey"),
    ("it is", "e dey"),
    ("they are", "dem dey"),
    ("he is", "him dey"),
    ("we are", "we dey"),
    ("i'm", "i dey"),
    ("are", "dey"),
    ("i had", "i don get"),
    ("i have", "i don"), 
    ("going", "dey go"),
    ("coming", "dey come"),
    ("i can", "i fit"),
    ("i could", "i fit"), 
    ("you", "yu"),
    ("just", "jus"),
]

# Function to apply replacements on text
def stylize_pidgin(text):
    for eng, pidgin in Replacements:  # Loop through replacements
        text = text.replace(eng, pidgin)  # Replace English with Pidgin
    return text


# -----------------  ElevenLabs API Call -----------------

def text_to_speech(text, voice_id, output_path="output.mp3"):
    """
    Convert text → speech using ElevenLabs API.
    Saves audio to output.mp3
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"  # Voice endpoint
    headers = {
        "xi-api-key": API_KEY,             # Authentication
        "Content-Type": "application/json" # Sending JSON payload
    }
    payload = {
        "text": text,  # The text to be spoken
        "voice_settings": {
            "stability": 0.75,        # Controls variation
            "similarity_boost": 0.75  # Controls closeness to real voice
        }
    }
    response = requests.post(url, json=payload, headers=headers)  # Send POST request
    if response.status_code == 200:  # ✅ Success
        with open(output_path, "wb") as f:  # Save audio file
            f.write(response.content)
        return output_path
    else:  # ❌ Error
        st.error(f"❌ Error: {response.status_code} - {response.text}")
        return None


# -----------------  Streamlit UI -----------------

# Try fetching API key from Streamlit secrets
try:
    elevenlabs_api_key = st.secrets["ELEVENLABS_API_KEY"]
except KeyError:
    st.error("ElevenLabs API key not found in Streamlit secrets. Please add it to your app's secrets.")
    st.stop()

# App title
st.title("🗣️ ElevenLabs TTS App with Nigerian Pidgin & Accent Filter")


# Step 1: Fetch voices
voice_map = get_voices()

# Step 2: Add custom voices (hardcoded voice IDs)
custom_voices = {
    "Fisayo": "it5NMxoQQ2INIh4XcO44",
    "Olabisi": "eOHsvebhdtt0XFeHVMQY",
    "timi": "yp4MmTRKvE7VXY3hUJRY"
}
# Remove old versions of same names
for name in custom_voices:
    voice_map.pop(name, None)
# Add new voices
voice_map.update(custom_voices)
voice_accents.update({
    "Fisayo": "Nigerian",
    "Olabisi": "Nigerian",
    "timi": "Nigerian"
})

# If no voices, stop app
if not voice_map:
    st.stop()


# Step 3: Accent Filter
accent_options = ["All", "Nigerian", "African", "American", "British"]  # Filter categories
selected_accent = st.selectbox("🌐 Filter voices by accent:", accent_options)  # Dropdown

# Filter voices based on accent selection
filtered_voices = (
    voice_map if selected_accent == "All" else {
        name: vid for name, vid in voice_map.items()
        if voice_accents.get(name, "Unknown") == selected_accent
    }
)

# If no voices found for selected accent
if not filtered_voices:
    st.warning("No voices found for selected accent.")
    st.stop()


# Step 4: Voice Selection
voice_names = sorted(filtered_voices.keys())  # Sort names alphabetically
selected_voice = st.selectbox("🎤 Choose a voice:", voice_names, index=0)  # Dropdown for voices
selected_voice_id = filtered_voices[selected_voice]  # Get voice ID


# Step 5: Preview (fetch preview URL for selected voice)
preview_url = f"https://api.elevenlabs.io/v1/voices/{selected_voice_id}"
headers = {"xi-api-key": API_KEY}
res = requests.get(preview_url, headers=headers)
if res.status_code == 200 and "preview_url" in res.json():
    st.audio(res.json()["preview_url"], format="audio/mp3")  # Play preview if available


# -----------------  User Input and Controls -----------------

st.markdown("## 📝 Enter Your Text")

# Text area for user input
text_input = st.text_area("Type your text here:", height=150, key="input_text_area")

# Two checkboxes side by side
col1, col2 = st.columns(2)
with col1:
    pidgin_mode = st.checkbox("🗣️ Auto-style for Nigerian Pidgin", value=False)  # Toggle Pidgin
with col2:
    show_changes = st.checkbox("👁️ Show English ➝ Pidgin replacements", value=False)  # Toggle showing changes


# If Pidgin mode is enabled
if pidgin_mode and text_input.strip():
    stylized_text = stylize_pidgin(text_input)  # Convert English → Pidgin

    # If user wants to see replacements
    if show_changes:
        st.markdown("### 🔤 English ➝ Pidgin Replacements")
        changes = []
        for eng, pidgin in Replacements:  # Check which words were replaced
            if eng in text_input:
                changes.append(f"- `{eng}` ➝ `{pidgin}`")
        if changes:
            st.markdown("\n".join(changes))  # Show changes
        else:
            st.info("ℹ️ No substitutions found.")

    # Show final Pidgin text
    st.markdown("### 🗣️ Stylized Pidgin Text")
    st.code(stylized_text, language="text")
else:
    stylized_text = text_input  # If not using Pidgin mode, keep text as is


# -----------------  Generate Audio -----------------

st.markdown("## 🔊 Generate Audio")

# Button to generate audio
if st.button("🎙️ Generate Audio"):
    if not text_input.strip():  # Empty text check
        st.warning("⚠️ Please enter some text.")
    else:
        with st.spinner("🔄 Generating audio..."):  # Loading spinner
            audio_file = text_to_speech(stylized_text, selected_voice_id)  # Call API
            if audio_file:  # If success
                st.audio(audio_file, format="audio/mp3")  # Play audio
                with open(audio_file, "rb") as f:  # Open audio file
                    st.download_button(
                        label="⬇️ Download Audio",  # Button to download
                        data=f,
                        file_name="tts_output.mp3",
                        mime="audio/mpeg"
                    )
                st.success("✅ Audio generated successfully!")  # Success message
