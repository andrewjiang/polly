#!/usr/bin/env python3
"""
Polly - Voice Assistant using OpenAI's Realtime API

This script implements a voice assistant that:
1. Waits for the user to press Enter
2. Records audio and streams it to OpenAI's Realtime API
3. Plays back the audio response in real-time
4. Provides text transcripts of the conversation
"""

import os
import time
import logging
import threading
import signal
import sys
import asyncio
from dotenv import load_dotenv
import elevenlabs
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("polly.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Audio device constants
HEADPHONE_DEVICE = os.environ.get("AUDIO_PLAYBACK_DEVICE", "hw:2,0")  # Raspberry Pi headphone jack
RECORDING_DEVICE = os.environ.get("AUDIO_RECORDING_DEVICE", "hw:3,0")  # USB microphone

# Eleven Labs API key
ELEVEN_LABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not ELEVEN_LABS_API_KEY:
    logger.error("Eleven Labs API key not set")
    sys.exit(1)

# Initialize the Eleven Labs client
client = ElevenLabs(api_key=ELEVEN_LABS_API_KEY)

# Callback for when the agent responds
async def agent_response_callback(response):
    print(f"Agent: {response}")
    # Wait for a short period after the agent finishes speaking
    await asyncio.sleep(2)  # Adjust the delay as needed

# Initialize the Conversation instance with the callback
conversation = Conversation(
    client,
    os.getenv("AGENT_ID"),
    requires_auth=bool(ELEVEN_LABS_API_KEY),
    audio_interface=DefaultAudioInterface(),
    callback_agent_response=agent_response_callback,
    callback_agent_response_correction=lambda original, corrected: print(f"Agent: {original} -> {corrected}"),
    callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
)

# Audio settings
CHANNELS = 1  # Mono
SAMPLE_RATE = 16000  # 16kHz

def play_audio_file(audio_file, device=HEADPHONE_DEVICE):
    """
    Play an audio file (automatically detects format).
    
    Args:
        audio_file (str): Path to the audio file
        device (str): Audio device to use for playback
        
    Returns:
        bool: True if playback was successful, False otherwise
    """
    import subprocess
    
    if not os.path.exists(audio_file):
        logger.error(f"Audio file not found: {audio_file}")
        return False
        
    # Determine file type based on extension
    file_ext = os.path.splitext(audio_file)[1].lower()
    
    if file_ext == '.wav':
        logger.info(f"Playing WAV: {audio_file} on device {device}")
        try:
            # Set volume to maximum before playback
            subprocess.run(["amixer", "-c", "2", "set", "PCM", "100%"], check=False)
            
            # Play the WAV file
            subprocess.run(["aplay", "-D", device, audio_file], check=True)
            return True
        except Exception as e:
            logger.error(f"Error playing WAV file: {e}")
            return False
    elif file_ext == '.mp3':
        logger.info(f"Playing MP3: {audio_file} on device {device}")
        try:
            # Play the MP3 file
            subprocess.run(["mpg123", "-a", device, audio_file], check=True)
            logger.info("Playback complete")
            return True
        except Exception as e:
            logger.error(f"Error playing MP3 file: {e}")
            return False
    else:
        logger.error(f"Unsupported audio format: {file_ext}")
        return False

def play_beep():
    """Play a beep sound to indicate recording start/stop."""
    beep_path = "audio/responses/beep.wav"
    
    # Check if beep.wav exists
    if not os.path.exists(beep_path):
        logger.warning(f"{beep_path} not found, creating it")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(beep_path), exist_ok=True)
        
        # Try to create a beep using speaker-test and arecord
        try:
            subprocess.run([
                "bash", "-c",
                "speaker-test -t sine -f 1000 -l 1 & pid=$!; "
                "sleep 0.3; "
                "arecord -d 1 -f cd -t wav -D hw:2,0 audio/responses/beep.wav; "
                "kill $pid"
            ], check=True)
        except Exception as e:
            logger.error(f"Error creating beep.wav: {e}")
            return False
    
    # Play the beep
    return play_audio_file(beep_path)

def ensure_directories():
    """Ensure necessary directories exist."""
    os.makedirs("audio", exist_ok=True)
    os.makedirs("audio/responses", exist_ok=True)
    os.makedirs("audio/recordings", exist_ok=True)

def handle_exit(signal, frame):
    """Handle exit signals gracefully."""
    logger.info("Exiting...")
    sys.exit(0)

class AudioPlayer:
    """Simple audio player for streaming audio data."""
    
    def __init__(self):
        self.buffer = b""
        self.playing = False
        self.thread = None
        
    def add_data(self, data):
        """Add audio data to the buffer."""
        self.buffer += data
        
        # Start playback if not already playing
        if not self.playing:
            self.start_playback()
    
    def start_playback(self):
        """Start playing audio from the buffer."""
        if self.playing:
            return
            
        self.playing = True
        self.thread = threading.Thread(target=self._playback_thread)
        self.thread.daemon = True
        self.thread.start()
    
    def _playback_thread(self):
        """Thread for playing audio data."""
        try:
            import tempfile
            import os
            
            # Create a temporary file for the audio data
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                
            # Keep playing chunks as they come in
            while True:
                if len(self.buffer) > 4000:  # Play in chunks of ~0.25 seconds
                    chunk = self.buffer[:4000]
                    self.buffer = self.buffer[4000:]
                    
                    # Write chunk to temporary file
                    with open(temp_path, "wb") as f:
                        # Simple WAV header for raw PCM data
                        # This is a very basic header and might need adjustment
                        f.write(b"RIFF")
                        f.write((36 + len(chunk)).to_bytes(4, 'little'))
                        f.write(b"WAVE")
                        f.write(b"fmt ")
                        f.write((16).to_bytes(4, 'little'))
                        f.write((1).to_bytes(2, 'little'))  # PCM format
                        f.write((CHANNELS).to_bytes(2, 'little'))
                        f.write((SAMPLE_RATE).to_bytes(4, 'little'))
                        f.write((SAMPLE_RATE * CHANNELS * 2).to_bytes(4, 'little'))
                        f.write((CHANNELS * 2).to_bytes(2, 'little'))
                        f.write((16).to_bytes(2, 'little'))
                        f.write(b"data")
                        f.write((len(chunk)).to_bytes(4, 'little'))
                        f.write(chunk)
                    
                    # Play the chunk
                    play_audio_file(temp_path)
                    
                elif not self.buffer:
                    # No more data, stop playback
                    break
                else:
                    # Wait for more data
                    time.sleep(0.1)
            
            # Clean up
            try:
                os.unlink(temp_path)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error in audio playback: {e}")
        finally:
            self.playing = False

async def elevenlabs_conversation():
    """
    Run a conversation with Eleven Labs' Conversational AI.
    """
    try:
        # Define is_recording within the function scope
        is_recording = False

        # Start the conversation session
        conversation.start_session()

        # Function to handle user input in a separate thread
        def input_thread():
            nonlocal is_recording
            while True:
                cmd = input("Press Enter to start/stop conversation, or 'q' to quit: ")
                if cmd.lower() == 'q':
                    print("Quitting...")
                    os._exit(0)  # Force exit
                else:
                    is_recording = not is_recording
                    if is_recording:
                        print("Conversation started... (Press Enter to stop)")
                        play_beep()
                    else:
                        print("Conversation stopped.")
                        play_beep()

        # Start input thread
        input_thread = threading.Thread(target=input_thread)
        input_thread.daemon = True
        input_thread.start()

        # Main event loop
        while True:
            if is_recording:
                # Wait for the conversation to end
                conversation_id = conversation.wait_for_session_end()
                print(f"Conversation ID: {conversation_id}")

            # Small sleep to prevent CPU hogging
            await asyncio.sleep(0.01)

    except Exception as e:
        logger.error(f"Error in Eleven Labs conversation: {e}")
        print(f"Error: {e}")

    finally:
        # End the conversation session
        conversation.end_session()

# Update main function to use Eleven Labs
async def main():
    """Main entry point."""
    logger.info("Starting Polly voice assistant with Eleven Labs Conversational AI")

    # Register signal handlers
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Ensure directories exist
    ensure_directories()

    # Run the Eleven Labs conversation
    try:
        await elevenlabs_conversation()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        print(f"Error: {e}")

    logger.info("Exiting Polly")
    return 0

if __name__ == "__main__":
    asyncio.run(main())
