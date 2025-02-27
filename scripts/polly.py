#!/usr/bin/env python3
"""
Polly - Voice Assistant

This is the main application file that integrates all components:
- Button handling for user interaction
- Audio recording and playback
- Speech-to-text using OpenAI Whisper
- Conversational AI using OpenAI ChatGPT
- Text-to-speech using OpenAI TTS
"""

import os
import time
import logging
import signal
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import custom modules
from hardware.button import ButtonHandler
from audio_utils import play_audio_file, record_audio
from api.openai_api import transcribe_audio, get_chatgpt_response
from api.tts_api import generate_speech

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

# Constants
BUTTON_PIN = 17  # GPIO pin for the button
LED_PIN = 27     # GPIO pin for the LED
RECORDING_DURATION = 10  # Maximum recording duration in seconds
AUDIO_DIR = Path("audio")
RECORDINGS_DIR = AUDIO_DIR / "recordings"
RESPONSES_DIR = AUDIO_DIR / "responses"

# Ensure directories exist
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
RESPONSES_DIR.mkdir(parents=True, exist_ok=True)

class Polly:
    """Main Polly voice assistant class."""
    
    def __init__(self):
        """Initialize Polly voice assistant."""
        logger.info("Initializing Polly voice assistant")
        
        # Initialize button handler
        self.button_handler = ButtonHandler(
            button_pin=BUTTON_PIN,
            led_pin=LED_PIN,
            button_callback=self.process_button_press
        )
        
        # Flag to indicate if Polly is currently processing
        self.is_processing = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        
        # Play startup sound
        self.play_startup_sound()
    
    def play_startup_sound(self):
        """Play a startup sound to indicate Polly is ready."""
        startup_sound = RESPONSES_DIR / "startup.mp3"
        if not startup_sound.exists():
            # Generate a startup message if the file doesn't exist
            generate_speech("Polly is now online and ready to assist you.", str(startup_sound))
        
        play_audio_file(str(startup_sound))
    
    def process_button_press(self):
        """Handle button press event."""
        if self.is_processing:
            logger.info("Already processing a request, ignoring button press")
            return
        
        try:
            self.is_processing = True
            
            # 1. Record audio
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            recording_file = RECORDINGS_DIR / f"recording_{timestamp}.wav"
            
            logger.info(f"Recording audio to {recording_file}")
            record_audio(str(recording_file), RECORDING_DURATION)
            
            # 2. Transcribe audio
            transcription = transcribe_audio(str(recording_file))
            if not transcription or transcription.lower() in ["i couldn't understand the audio. could you please try again?"]:
                # Play error sound or message
                error_message = "I couldn't understand what you said. Could you please try again?"
                error_file = RESPONSES_DIR / "error_understanding.mp3"
                generate_speech(error_message, str(error_file))
                play_audio_file(str(error_file))
                self.is_processing = False
                return
            
            # 3. Get response from ChatGPT
            response_text = get_chatgpt_response(transcription)
            
            # 4. Convert response to speech
            response_file = RESPONSES_DIR / f"response_{timestamp}.mp3"
            speech_file = generate_speech(response_text, str(response_file))
            
            if speech_file:
                # 5. Play the response
                play_audio_file(speech_file)
            else:
                # Play error message
                error_message = "I'm having trouble generating a response. Please try again later."
                error_file = RESPONSES_DIR / "error_response.mp3"
                generate_speech(error_message, str(error_file))
                play_audio_file(str(error_file))
        
        except Exception as e:
            logger.error(f"Error processing button press: {str(e)}")
            # Play error sound
            error_file = RESPONSES_DIR / "error.mp3"
            if not error_file.exists():
                generate_speech("Sorry, I encountered an error. Please try again.", str(error_file))
            play_audio_file(str(error_file))
        
        finally:
            self.is_processing = False
    
    def run(self):
        """Run the main loop of Polly."""
        logger.info("Polly is running. Press Ctrl+C to exit.")
        
        try:
            # Start the button handler
            self.button_handler.start()
            
            # Keep the main thread alive
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            self.cleanup()
    
    def cleanup(self, signum=None, frame=None):
        """Clean up resources and exit gracefully."""
        logger.info("Cleaning up resources")
        
        if hasattr(self, 'button_handler'):
            self.button_handler.stop()
        
        logger.info("Polly is shutting down")
        sys.exit(0)

if __name__ == "__main__":
    # Check for required API keys
    if not os.environ.get("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment variables")
        print("Error: OPENAI_API_KEY not found. Please set it in your .env file.")
        sys.exit(1)
    
    if not os.environ.get("ELEVEN_LABS_API_KEY"):
        logger.error("ELEVEN_LABS_API_KEY not found in environment variables")
        print("Error: ELEVEN_LABS_API_KEY not found. Please set it in your .env file.")
        sys.exit(1)
    
    # Create and run Polly
    polly = Polly()
    polly.run() 