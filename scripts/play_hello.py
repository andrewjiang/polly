#!/usr/bin/env python3
"""
Simple script to play hello.mp3 using pygame.
"""
import os
import time
import pygame
import subprocess

print("Starting audio test with headphone jack (card 2)...")

# First, set the volume to maximum
try:
    subprocess.run(["amixer", "-c", "2", "sset", "Master", "100%"], check=True)
    print("Volume set to maximum")
except Exception as e:
    print(f"Warning: Could not set volume: {e}")

# Set the SDL audio driver to ALSA
os.environ['SDL_AUDIODRIVER'] = 'alsa'

# Set the audio device to the headphone jack (card 2)
os.environ['AUDIODEV'] = 'hw:2,0'

print("Initializing pygame...")
# Initialize pygame with the correct parameters
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
print("Pygame initialized")

# Get the absolute path to the hello.mp3 file
script_dir = os.path.dirname(os.path.abspath(__file__))
hello_mp3_path = os.path.join(script_dir, "audio", "responses", "hello.mp3")

print(f"File exists: {os.path.exists(hello_mp3_path)}")
print(f"File size: {os.path.getsize(hello_mp3_path)} bytes")

# Play the sound
print(f"Playing {hello_mp3_path}...")
sound = pygame.mixer.Sound(hello_mp3_path)

# Set volume to maximum
sound.set_volume(1.0)
print(f"Sound volume set to maximum")

# Play multiple times to ensure it's heard
for i in range(3):
    print(f"Playing sound (attempt {i+1}/3)...")
    sound.play()
    
    # Wait for the sound to finish playing
    duration = sound.get_length()
    print(f"Sound duration: {duration} seconds")
    time.sleep(duration + 0.5)  # Add a small buffer
    
print("Playback complete")

# Also try playing with speaker-test as a fallback
print("Now trying with speaker-test...")
try:
    subprocess.run(["speaker-test", "-D", "hw:2,0", "-c2", "-t", "sine", "-f", "440", "-l", "1"], check=True)
    print("speaker-test completed")
except Exception as e:
    print(f"Error with speaker-test: {e}") 