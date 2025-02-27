#!/usr/bin/env python3
"""
Audio utility functions for Polly.

This module provides functions for playing and recording audio files.
It supports both MP3 and WAV formats for playback, and WAV format for recording.
"""

import os
import time
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('audio_utils')

# Audio device constants
HEADPHONE_DEVICE = "hw:2,0"  # Raspberry Pi headphone jack
USB_AUDIO_DEVICE = "hw:4,0"  # USB audio adapter

def play_wav(wav_file, device=HEADPHONE_DEVICE):
    """
    Play a WAV file using aplay.
    
    Args:
        wav_file (str): Path to the WAV file
        device (str): Audio device to use for playback
        
    Returns:
        bool: True if playback was successful, False otherwise
    """
    if not os.path.exists(wav_file):
        logger.error(f"WAV file not found: {wav_file}")
        return False
        
    logger.info(f"Playing WAV: {wav_file} on device {device}")
    
    try:
        # Set volume to maximum before playback
        subprocess.run(["amixer", "-c", "2", "set", "PCM", "100%"], check=False)
        
        # Play the WAV file - using a simpler command without additional options
        subprocess.run(["aplay", wav_file], check=True)
        return True
    except Exception as e:
        logger.error(f"Error playing WAV file: {e}")
        return False

def play_mp3(mp3_file, device=HEADPHONE_DEVICE):
    """
    Play an MP3 file using mpg123.
    
    Args:
        mp3_file (str): Path to the MP3 file
        device (str): Audio device to use for playback
        
    Returns:
        bool: True if playback was successful, False otherwise
    """
    if not os.path.exists(mp3_file):
        logger.error(f"MP3 file not found: {mp3_file}")
        return False
        
    logger.info(f"Playing MP3: {mp3_file} on device {device}")
    
    try:
        # Play the MP3 file
        subprocess.run(["mpg123", "-a", device, mp3_file], check=True)
        logger.info("Playback complete: ")
        return True
    except Exception as e:
        logger.error(f"Error playing MP3 file: {e}")
        return False

def play_audio_file(audio_file, device=HEADPHONE_DEVICE):
    """
    Play an audio file (automatically detects format).
    
    Args:
        audio_file (str): Path to the audio file
        device (str): Audio device to use for playback
        
    Returns:
        bool: True if playback was successful, False otherwise
    """
    if not os.path.exists(audio_file):
        logger.error(f"Audio file not found: {audio_file}")
        return False
        
    # Determine file type based on extension
    file_ext = os.path.splitext(audio_file)[1].lower()
    
    if file_ext == '.wav':
        return play_wav(audio_file, device)
    elif file_ext == '.mp3':
        return play_mp3(audio_file, device)
    else:
        logger.error(f"Unsupported audio format: {file_ext}")
        return False

def record_audio(output_file=None, duration=5, device=USB_AUDIO_DEVICE):
    """
    Record audio using arecord.
    
    Note: This method is not recommended for production use as it may produce glitchy recordings.
    Consider using the AudioRecorder class from hardware.audio instead.
    
    Args:
        output_file (str): Path to save the recording (default: auto-generated)
        duration (int): Recording duration in seconds
        device (str): Audio device to use for recording
        
    Returns:
        str: Path to the recorded file if successful, None otherwise
    """
    # Generate output filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"audio/test_recording_{timestamp}.wav"
        
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    logger.info(f"Recording to {output_file} for {duration} seconds...")
    
    try:
        # Record audio
        subprocess.run([
            "arecord", 
            "-D", device,
            "-d", str(duration),
            "-f", "cd",  # CD quality (16-bit, 44100Hz, stereo)
            "-t", "wav", 
            output_file
        ], check=True)
        
        logger.info(f"Recording saved to {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error recording audio: {e}")
        return None

def play_pygame(audio_file):
    """
    Play an audio file using pygame.
    
    Args:
        audio_file (str): Path to the audio file
        
    Returns:
        bool: True if playback was successful, False otherwise
    """
    if not os.path.exists(audio_file):
        logger.error(f"Audio file not found: {audio_file}")
        return False
        
    try:
        import pygame
        pygame.mixer.init()
        
        # Determine file type based on extension
        file_ext = os.path.splitext(audio_file)[1].lower()
        
        if file_ext == '.wav':
            # For WAV files, use Sound
            sound = pygame.mixer.Sound(audio_file)
            sound.play()
            time.sleep(sound.get_length())
        elif file_ext == '.mp3':
            # For MP3 files, use music
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        else:
            logger.error(f"Unsupported audio format for pygame: {file_ext}")
            pygame.mixer.quit()
            return False
            
        pygame.mixer.quit()
        return True
    except ImportError:
        logger.error("pygame module not available")
        return False
    except Exception as e:
        logger.error(f"Error playing audio with pygame: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Test WAV playback
    wav_file = "audio/responses/beep.wav"
    if os.path.exists(wav_file):
        print(f"Testing WAV playback: {wav_file}")
        play_wav(wav_file)
    
    # Test MP3 playback
    mp3_file = "audio/responses/hello.mp3"
    if os.path.exists(mp3_file):
        print(f"Testing MP3 playback: {mp3_file}")
        play_mp3(mp3_file)
    
    # Test recording
    print("Testing recording (5 seconds)...")
    recorded_file = record_audio(duration=5)
    if recorded_file:
        print(f"Playing back recording: {recorded_file}")
        play_wav(recorded_file) 