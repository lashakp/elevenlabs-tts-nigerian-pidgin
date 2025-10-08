# utils/api.py
import requests
from typing import Dict, Optional
from time import sleep
from requests.exceptions import RequestException
import streamlit as st

@st.cache_resource(show_spinner=False)
def get_voices(api_key: str) -> Dict[str, str]:
    """
    Fetch available voices from ElevenLabs API.
    Args:
        api_key (str): ElevenLabs API key.
    Returns:
        Dict[str, str]: Dictionary of voice names to voice IDs.
    """
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices = response.json()["voices"]
        return {voice["name"]: voice["voice_id"] for voice in voices}
    else:
        st.error(f"❌ Failed to fetch voices: {response.status_code}")
        return {}

@st.cache_data(show_spinner=False)
def get_voice_preview(voice_id: str, api_key: str) -> Optional[str]:
    """
    Fetch preview URL for a specific voice.
    Args:
        voice_id (str): Voice ID.
        api_key (str): ElevenLabs API key.
    Returns:
        Optional[str]: Preview URL or None if not found.
    """
    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
    headers = {"xi-api-key": api_key}
    res = requests.get(url, headers=headers)
    return res.json().get("preview_url") if res.status_code == 200 and "preview_url" in res.json() else None

def validate_api_key(api_key: str) -> bool:
    """
    Validate the ElevenLabs API key.
    Args:
        api_key (str): API key to validate.
    Returns:
        bool: True if valid, False otherwise.
    """
    url = "https://api.elevenlabs.io/v1/user"
    headers = {"xi-api-key": api_key}
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def text_to_speech(text: str, voice_id: str, api_key: str, output_path: str = "output.mp3", 
                   stability: float = 0.75, similarity_boost: float = 0.75, max_retries: int = 3) -> Optional[str]:
    """
    Convert text to speech using ElevenLabs API with retry logic.
    Args:
        text (str): Text to convert.
        voice_id (str): Voice ID.
        api_key (str): API key.
        output_path (str): Path to save audio.
        stability (float): Voice stability setting.
        similarity_boost (float): Voice similarity setting.
        max_retries (int): Max retry attempts for rate limits.
    Returns:
        Optional[str]: Path to audio file or None on failure.
    """
    CHUNK_SIZE = 1000
    if len(text) > CHUNK_SIZE:
        st.warning("Text is long; splitting into chunks.")
        chunks = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
        combined_audio = b''
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
        for chunk in chunks:
            payload = {
                "text": chunk,
                "voice_settings": {"stability": stability, "similarity_boost": similarity_boost}
            }
            for attempt in range(max_retries):
                try:
                    response = requests.post(url, json=payload, headers=headers)
                    if response.status_code == 200:
                        combined_audio += response.content
                        break
                    elif response.status_code == 429:
                        st.warning("Rate limit hit. Retrying...")
                        sleep(2 ** attempt)
                    elif response.status_code == 401:
                        st.error("❌ Invalid API key. Please check your ElevenLabs API key.")
                        return None
                    elif response.status_code == 402:
                        st.error("❌ API quota exceeded. Try again later or upgrade your ElevenLabs plan.")
                        return None
                    else:
                        st.error(f"❌ Error: {response.status_code} - {response.text}")
                        return None
                except RequestException as e:
                    st.error(f"❌ Network error: {e}")
                    return None
            else:
                st.error("❌ Max retries exceeded.")
                return None
        with open(output_path, "wb") as f:
            f.write(combined_audio)
        return output_path
    else:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "voice_settings": {"stability": stability, "similarity_boost": similarity_boost}
        }
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    return output_path
                elif response.status_code == 429:
                    st.warning("Rate limit hit. Retrying...")
                    sleep(2 ** attempt)
                elif response.status_code == 401:
                    st.error("❌ Invalid API key. Please check your ElevenLabs API key.")
                    return None
                elif response.status_code == 402:
                    st.error("❌ API quota exceeded. Try again later or upgrade your ElevenLabs plan.")
                    return None
                else:
                    st.error(f"❌ Error: {response.status_code} - {response.text}")
                    return None
            except RequestException as e:
                st.error(f"❌ Network error: {e}")
                return None
        st.error("❌ Max retries exceeded.")
        return None