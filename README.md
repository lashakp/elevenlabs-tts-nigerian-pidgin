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
