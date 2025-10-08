# 🗣️ ElevenLabs TTS Web App (with Nigerian Pidgin & Accent Filter)

This is a Streamlit web application that uses the [ElevenLabs Text-to-Speech API](https://www.elevenlabs.io/) to convert text into audio. It includes:

LATEST UPDATE:

# ElevenLabs TTS App

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Add `ELEVENLABS_API_KEY` to `.env` or Streamlit secrets.
3. Run: `streamlit run app.py`

## Features
- Text-to-speech with ElevenLabs API
- Nigerian Pidgin conversion with case preservation
- Accent filtering for voices
- Custom Pidgin replacements
- Advanced voice settings (stability, similarity boost)
- Audio playback speed control
- History of generated audio
- Batch processing via text file upload

## Testing
Run `python -m unittest discover tests`

## Recent Changes
- Fixed case preservation in Pidgin conversion (Oct 08, 2025).
- Added `__init__.py` to `utils` for package structure.


- ✅ Voice selection with accent filters (British, African, Nigerian, etc.)
- ✅ Support for Nigerian Pidgin styling
- ✅ Custom Nigerian voice integration
- ✅ Audio preview and download

---

## 🚀 Features

- 🎙️ Select from available ElevenLabs voices or use custom Nigerian ones
- 🌍 Filter voices by accent: Nigerian, African, American, British
- 🗣️ Convert English or Nigerian Pidgin text to speech
- 🎧 Audio player with download button
- 🔄 Preview voice sample before generating

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/lashakp/elevenlabs-tts-nigerian-pidgin.git
cd elevenlabs-tts-nigerian-pidgin

custom_voices = {
    "Fisayo": "it5NMxoQQ2INIh4XcO44",
    "Olabisi": "eOHsvebhdtt0XFeHVMQY",
    "timi": "yp4MmTRKvE7VXY3hUJRY"
}




















---
title: Eleven Labs Tts
emoji: 📈
colorFrom: gray
colorTo: gray
sdk: docker
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference
