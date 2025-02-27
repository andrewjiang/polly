"""
Text-to-Speech API integration for Polly.

This module provides functions to interact with OpenAI's API for text-to-speech conversion.
It includes a fallback mechanism for when the API call fails.
"""

import os
import logging
import time
import wave
import array
import math
from pathlib import Path
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OpenAI API configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Default voice
DEFAULT_VOICE = "alloy"  # OpenAI voices: alloy, echo, fable, onyx, nova, shimmer

# Audio output directory
AUDIO_OUTPUT_DIR = Path("audio/responses")

# Initialize OpenAI client
try:
    client = OpenAI()  # Uses OPENAI_API_KEY from environment by default
except TypeError as e:
    # Handle the case where 'proxies' argument is not supported
    if 'unexpected keyword argument' in str(e) and 'proxies' in str(e):
        logger.warning("OpenAI client initialization failed with proxies argument. Using default initialization.")
        import httpx
        # Create a custom httpx client without proxies
        http_client = httpx.Client()
        client = OpenAI(http_client=http_client)
    else:
        # Re-raise if it's a different TypeError
        raise

def generate_fallback_audio(output_file, duration=1.0, frequency=440.0, volume=0.5):
    """
    Generate a simple beep sound as a fallback when TTS API fails.
    
    Args:
        output_file (str): Path to save the audio file
        duration (float): Duration of the beep in seconds
        frequency (float): Frequency of the beep in Hz
        volume (float): Volume of the beep (0.0 to 1.0)
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        # Audio parameters
        sample_rate = 44100  # Hz
        num_samples = int(duration * sample_rate)
        
        # Generate sine wave
        samples = array.array('h')
        amplitude = int(32767 * volume)
        
        for i in range(num_samples):
            sample = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
            samples.append(int(sample))
        
        # Save as WAV file
        output_file = str(output_file)
        if output_file.endswith('.mp3'):
            output_file = output_file.replace('.mp3', '.wav')
            
        with wave.open(output_file, 'w') as wav_file:
            wav_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
            wav_file.writeframes(samples.tobytes())
        
        logger.info(f"Generated fallback audio at {output_file}")
        return output_file
    
    except Exception as e:
        logger.error(f"Error generating fallback audio: {str(e)}")
        return None

def generate_speech(text, output_file=None, voice=None):
    """
    Generate speech from text using OpenAI's text-to-speech API.
    Falls back to a simple beep sound if the API call fails.
    
    Args:
        text (str): Text to convert to speech
        output_file (str, optional): Path to save the audio file. If None, a default path will be generated.
        voice (str, optional): OpenAI voice to use. Options: alloy, echo, fable, onyx, nova, shimmer
        
    Returns:
        str: Path to the generated audio file
    """
    try:
        if not OPENAI_API_KEY:
            logger.error("OpenAI API key not found in environment variables")
            return None
        
        # Ensure output directory exists
        AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate output filename if not provided
        if not output_file:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = AUDIO_OUTPUT_DIR / f"response_{timestamp}.mp3"
        else:
            output_file = Path(output_file)
            if not output_file.is_absolute():
                output_file = AUDIO_OUTPUT_DIR / output_file
        
        # Use default voice if not specified
        if not voice:
            voice = DEFAULT_VOICE
        
        logger.info(f"Generating speech for text: {text[:50]}...")
        
        try:
            # Make API request
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            # Save the audio file
            response.stream_to_file(str(output_file))
            
            logger.info(f"Speech generated successfully and saved to {output_file}")
            return str(output_file)
        
        except Exception as e:
            logger.error(f"Error in OpenAI TTS API call: {str(e)}")
            logger.info("Falling back to generating a simple beep sound...")
            return generate_fallback_audio(output_file)
    
    except Exception as e:
        logger.error(f"Error in generate_speech: {str(e)}")
        return None

def list_available_voices():
    """
    List all available voices from OpenAI's TTS API.
    
    Returns:
        list: List of available voices
    """
    # OpenAI has a fixed set of voices
    voices = [
        {"voice_id": "alloy", "name": "Alloy", "description": "Versatile, balanced voice"},
        {"voice_id": "echo", "name": "Echo", "description": "Soft, warm voice"},
        {"voice_id": "fable", "name": "Fable", "description": "Narrative, soothing voice"},
        {"voice_id": "onyx", "name": "Onyx", "description": "Deep, authoritative voice"},
        {"voice_id": "nova", "name": "Nova", "description": "Energetic, bright voice"},
        {"voice_id": "shimmer", "name": "Shimmer", "description": "Clear, optimistic voice"}
    ]
    
    return voices

if __name__ == "__main__":
    # Test the module
    test_output = generate_speech("Hello, I am Polly. How can I help you today?", "test_speech.mp3")
    if test_output:
        print(f"Test speech generated at: {test_output}")
    
    # List available voices
    voices = list_available_voices()
    if voices:
        print("\nAvailable voices:")
        for voice in voices:
            print(f"ID: {voice['voice_id']}, Name: {voice['name']}, Description: {voice['description']}") 