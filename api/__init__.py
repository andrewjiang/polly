"""
API integration module for Polly.

This package contains modules for interacting with external APIs:
- openai_api.py: OpenAI API integration (Whisper and ChatGPT)
- tts_api.py: Text-to-speech API integration (Eleven Labs)
"""

from api.openai_api import transcribe_audio, get_chatgpt_response
from api.tts_api import generate_speech

__all__ = ['transcribe_audio', 'get_chatgpt_response', 'generate_speech'] 