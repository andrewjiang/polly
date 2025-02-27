#!/usr/bin/env python3
"""
Functionality test script for Polly.

This script provides separate functions to test different aspects of the audio system:
1. MP3 playback (hello.mp3)
2. WAV playback (beep.wav)
3. Audio recording (5 seconds)

Usage:
    python functionality_test.py --test mp3
    python functionality_test.py --test wav
    python functionality_test.py --test record
    python functionality_test.py --test all
"""

import os
import sys
import time
import wave
import argparse
import subprocess
from datetime import datetime

# Audio device constants
HEADPHONE_DEVICE = "hw:2,0"  # Raspberry Pi headphone jack
USB_AUDIO_DEVICE = "hw:4,0"  # USB audio adapter
# Add a recording device - try a different device that might work better
RECORDING_DEVICE = "hw:3,0"  # Try a different device for recording

def ensure_directories():
    """Ensure necessary directories exist."""
    os.makedirs("audio", exist_ok=True)
    os.makedirs("audio/responses", exist_ok=True)

def create_beep_wav():
    """Create a simple beep.wav file if it doesn't exist."""
    beep_path = "audio/responses/beep.wav"
    
    if os.path.exists(beep_path):
        print(f"Using existing {beep_path}")
        return beep_path
        
    print(f"Creating {beep_path}...")
    
    # Generate a simple beep using speaker-test and arecord
    try:
        # Create a 1-second 1000Hz beep
        subprocess.run([
            "bash", "-c",
            "speaker-test -t sine -f 1000 -l 1 & pid=$!; "
            "sleep 0.3; "
            "arecord -d 1 -f cd -t wav -D hw:2,0 audio/responses/beep.wav; "
            "kill $pid"
        ], check=True)
        print(f"Created {beep_path}")
    except Exception as e:
        print(f"Error creating beep.wav: {e}")
        
        # Create an empty WAV file as fallback
        try:
            # Create a 1-second silent WAV file
            rate = 44100
            frames = [b'\x00\x00' * rate]
            with wave.open(beep_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(rate)
                wf.writeframes(b''.join(frames))
            print(f"Created silent {beep_path} as fallback")
        except Exception as e2:
            print(f"Error creating fallback beep.wav: {e2}")
            return None
            
    return beep_path

def test_mp3_playback():
    """Test MP3 playback using hello.mp3."""
    print("\n=== Testing MP3 Playback ===")
    
    # Check if hello.mp3 exists
    hello_mp3_path = "audio/responses/hello.mp3"
    if not os.path.exists(hello_mp3_path):
        print(f"Error: {hello_mp3_path} does not exist")
        return False
        
    print(f"Found {hello_mp3_path}")
    
    # Method 1: Using mpg123 directly
    print("\nMethod 1: Using mpg123 directly")
    try:
        subprocess.run(["mpg123", "-a", HEADPHONE_DEVICE, hello_mp3_path], check=True)
        print("✅ mpg123 playback successful")
    except Exception as e:
        print(f"❌ mpg123 playback failed: {e}")
        
    # Method 2: Using audio_utils if available
    print("\nMethod 2: Using audio_utils")
    try:
        from audio_utils import play_mp3
        result = play_mp3(hello_mp3_path, HEADPHONE_DEVICE)
        if result:
            print("✅ audio_utils.play_mp3 successful")
        else:
            print("❌ audio_utils.play_mp3 failed")
    except ImportError:
        print("❌ audio_utils module not available")
        
    # Method 3: Using pygame if available
    print("\nMethod 3: Using pygame")
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(hello_mp3_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        print("✅ pygame playback successful")
    except Exception as e:
        print(f"❌ pygame playback failed: {e}")
        
    return True

def test_wav_playback():
    """Test WAV playback using beep.wav."""
    print("\n=== Testing WAV Playback ===")
    
    # Ensure beep.wav exists
    beep_wav_path = create_beep_wav()
    if not beep_wav_path or not os.path.exists(beep_wav_path):
        print(f"Error: Failed to create or find beep.wav")
        return False
        
    print(f"Found {beep_wav_path}")
    
    # Method 1: Using aplay directly
    print("\nMethod 1: Using aplay directly")
    try:
        subprocess.run(["aplay", "-D", HEADPHONE_DEVICE, beep_wav_path], check=True)
        print("✅ aplay playback successful")
    except Exception as e:
        print(f"❌ aplay playback failed: {e}")
        
    # Method 2: Using audio_utils if available
    print("\nMethod 2: Using audio_utils")
    try:
        from audio_utils import play_wav
        result = play_wav(beep_wav_path, HEADPHONE_DEVICE)
        if result:
            print("✅ audio_utils.play_wav successful")
        else:
            print("❌ audio_utils.play_wav failed")
    except ImportError:
        print("❌ audio_utils module not available")
        
    # Method 3: Using pygame if available
    print("\nMethod 3: Using pygame")
    try:
        import pygame
        pygame.mixer.init()
        sound = pygame.mixer.Sound(beep_wav_path)
        sound.play()
        time.sleep(sound.get_length())
        pygame.mixer.quit()
        print("✅ pygame playback successful")
    except Exception as e:
        print(f"❌ pygame playback failed: {e}")
        
    return True

def test_recording():
    """Test audio recording for 5 seconds."""
    print("\n=== Testing Audio Recording ===")
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"audio/test_recording_{timestamp}.wav"
    
    # Method 1: Using arecord directly (not recommended - may produce glitchy recordings)
    print("\nMethod 1: Using arecord directly (not recommended)")
    print("Note: This method may produce glitchy recordings. Method 2 is recommended.")
    try_method_1 = False  # Set to True to try Method 1
    
    if try_method_1:
        try:
            print(f"Recording to {output_path} for 5 seconds...")
            subprocess.run([
                "arecord", 
                "-D", USB_AUDIO_DEVICE,
                "-d", "5",
                "-f", "cd",
                "-t", "wav", 
                output_path
            ], check=True)
            print(f"✅ arecord recording saved to {output_path}")
            
            # Set volume to maximum before playback
            subprocess.run(["amixer", "-c", "2", "set", "PCM", "100%"], check=True)
            
            # Play back the recording
            print("Playing back the recording...")
            subprocess.run(["aplay", "-D", HEADPHONE_DEVICE, output_path], check=True)
            print("✅ Playback completed")
        except Exception as e:
            print(f"❌ arecord recording or playback failed: {e}")
    else:
        print("Skipping Method 1 (direct arecord) - using Method 2 instead")
        
    # Method 2: Using hardware.audio (recommended method)
    print("\nMethod 2: Using hardware.audio (recommended)")
    try:
        from hardware.audio import AudioRecorder, AudioPlayer
        
        # Create recorder and player
        recorder = AudioRecorder(
            output_dir="audio",
            rate=16000,         # 16kHz sample rate
            channels=1,         # Mono
            silence_duration=2.0,  # Stop after 2 seconds of silence
            max_duration=10.0   # Maximum 10 seconds
        )
        player = AudioPlayer(responses_dir="audio/responses")
        
        print(f"Recording for 5 seconds using AudioRecorder...")
        # Start recording
        filename = recorder.start_recording()
        print(f"Started recording to: {filename}")
        
        # Wait for 5 seconds
        time.sleep(5)
        
        # Stop recording
        recorder.stop_recording()
        
        # Check if file exists
        if os.path.exists(filename):
            print(f"✅ AudioRecorder recording saved to {filename}")
            
            # Play back the recording using our AudioPlayer
            print("Playing back the recording using AudioPlayer...")
            player.play_audio_file(filename)
            
            # Also try direct playback with aplay for comparison
            print("Playing back the recording using aplay...")
            subprocess.run(["aplay", "-D", HEADPHONE_DEVICE, filename], check=True)
            
            print("✅ Playback attempts completed")
        else:
            print(f"❌ AudioRecorder recording failed: file not found at {filename}")
            
        # Clean up
        recorder.cleanup()
        player.cleanup()
    except ImportError:
        print("❌ hardware.audio module not available")
    except Exception as e:
        print(f"❌ AudioRecorder recording failed: {e}")
        
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test audio functionality for Polly")
    parser.add_argument("--test", choices=["mp3", "wav", "record", "all"], default="all",
                        help="Test to run (default: all)")
    args = parser.parse_args()
    
    # Ensure directories exist
    ensure_directories()
    
    # Run the specified test(s)
    if args.test == "mp3" or args.test == "all":
        test_mp3_playback()
        
    if args.test == "wav" or args.test == "all":
        test_wav_playback()
        
    if args.test == "record" or args.test == "all":
        test_recording()
        
    print("\nAll tests completed!")
    
if __name__ == "__main__":
    main()