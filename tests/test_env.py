#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print environment variables
print(f"OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY', 'Not set')[:20]}...")
print(f"AUDIO_PLAYBACK_DEVICE: {os.environ.get('AUDIO_PLAYBACK_DEVICE', 'Not set')}")
print(f"AUDIO_RECORDING_DEVICE: {os.environ.get('AUDIO_RECORDING_DEVICE', 'Not set')}") 