#!/usr/bin/env python3
"""
Test script for the TTS API.
"""

import os
import time
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Audio device constants
HEADPHONE_DEVICE = "hw:2,0"  # Raspberry Pi headphone jack
USB_AUDIO_DEVICE = "hw:4,0"  # USB audio adapter

# Print environment variables
print(f"OPENAI_API_KEY: {os.environ.get('OPENAI_API_KEY', 'Not set')[:20]}...")

# Import the TTS API
try:
    from api.tts_api import generate_speech, list_available_voices
    from audio_utils import play_audio_file, play_mp3
    
    print("Successfully imported TTS API")
    
    # List available voices
    voices = list_available_voices()
    print(f"Available voices: {len(voices)}")
    for voice in voices:
        print(f"  - {voice['name']} ({voice['voice_id']})")
    
    # Generate speech
    print("\nGenerating speech...")
    output = generate_speech("Hello, I am Polly. I am now using OpenAI for text to speech.", "test_openai_tts.mp3")
    if output:
        print(f"Generated speech at: {output}")
        
        # Verify file exists and has content
        if os.path.exists(output):
            file_size = os.path.getsize(output)
            print(f"File exists and is {file_size} bytes")
        else:
            print(f"Warning: File {output} does not exist!")
        
        # Try to set volume to maximum
        try:
            print("Setting volume to maximum...")
            subprocess.run(["amixer", "-c", "2", "set", "PCM", "100%"], check=False)
        except Exception as e:
            print(f"Warning: Could not set volume: {e}")
        
        # Play the generated audio using play_audio_file
        print("\nPlaying the generated audio with play_audio_file...")
        result = play_audio_file(output, HEADPHONE_DEVICE)
        if result:
            print("✅ Audio playback successful with play_audio_file")
        else:
            print("❌ Audio playback failed with play_audio_file")
        
        # Try direct playback with play_mp3
        print("\nPlaying the generated audio with play_mp3...")
        result = play_mp3(output, HEADPHONE_DEVICE)
        if result:
            print("✅ Audio playback successful with play_mp3")
        else:
            print("❌ Audio playback failed with play_mp3")
        
        # Try direct playback with mpg123
        print("\nPlaying the generated audio with direct mpg123 command...")
        try:
            subprocess.run(["mpg123", "-a", HEADPHONE_DEVICE, output], check=True)
            print("✅ Direct mpg123 playback successful")
        except Exception as e:
            print(f"❌ Direct mpg123 playback failed: {e}")
    else:
        print("Failed to generate speech")
        
except Exception as e:
    print(f"Error: {e}") 