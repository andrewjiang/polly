#!/usr/bin/env python3
"""
Button handler for Polly.

This module provides functionality to detect button presses and trigger actions.
"""

import os
import time
import RPi.GPIO as GPIO
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('hardware.button')

# Button configuration
BUTTON_PIN = 17  # GPIO pin connected to the button
LED_PIN = 18     # GPIO pin for LED indicator (future use)

# Audio paths
AUDIO_DIR = "audio"
RESPONSES_DIR = os.path.join(AUDIO_DIR, "responses")
FEEDBACK_SOUND = os.path.join(RESPONSES_DIR, "beep.wav")

# Ensure directories exist
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(RESPONSES_DIR, exist_ok=True)

class ButtonHandler:
    """
    Handler for button press events that triggers audio recording and processing.
    """
    
    def __init__(self, audio_utils=None):
        """
        Initialize the button handler.
        
        Args:
            audio_utils: Audio utilities module for playback and recording
        """
        self.audio_utils = audio_utils
        self.is_recording = False
        self.setup_gpio()
        
    def setup_gpio(self):
        """Set up GPIO pins for button and LED."""
        # Use BCM pin numbering
        GPIO.setmode(GPIO.BCM)
        
        # Set up button pin as input with pull-down resistor
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # Set up LED pin as output (for future use)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)
        
        # Add event detection for button press
        GPIO.add_event_detect(
            BUTTON_PIN, 
            GPIO.RISING, 
            callback=self.on_button_press, 
            bouncetime=300
        )
        
        logger.info(f"GPIO initialized. Button on pin {BUTTON_PIN}, LED on pin {LED_PIN}")
    
    def play_feedback_sound(self):
        """Play immediate feedback sound when button is pressed."""
        if self.audio_utils:
            self.audio_utils.play_wav(FEEDBACK_SOUND)
        else:
            # Fallback if audio_utils not provided
            try:
                subprocess.run(["aplay", FEEDBACK_SOUND], check=True)
                logger.info(f"Played feedback sound: {FEEDBACK_SOUND}")
            except Exception as e:
                logger.error(f"Error playing feedback sound: {e}")
    
    def start_recording(self):
        """Start recording audio."""
        if self.is_recording:
            logger.warning("Already recording, ignoring button press")
            return None
            
        self.is_recording = True
        GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on LED to indicate recording
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(AUDIO_DIR, f"recording_{timestamp}.wav")
        
        logger.info(f"Starting recording to {output_file}")
        
        if self.audio_utils:
            # Use audio_utils if available
            recorded_file = self.audio_utils.record_audio(output_file)
        else:
            # Fallback to direct subprocess call
            try:
                # Record for 5 seconds (in a real implementation, we'd use silence detection)
                subprocess.run([
                    "arecord", 
                    "-D", "hw:4,0",  # USB audio device
                    "-d", "5",       # Duration in seconds
                    "-f", "cd",      # Format (CD quality)
                    "-t", "wav", 
                    output_file
                ], check=True)
                recorded_file = output_file
                logger.info(f"Recording saved to {output_file}")
            except Exception as e:
                logger.error(f"Error recording audio: {e}")
                recorded_file = None
        
        self.is_recording = False
        GPIO.output(LED_PIN, GPIO.LOW)  # Turn off LED
        
        return recorded_file
    
    def on_button_press(self, channel):
        """
        Callback function for button press event.
        
        Args:
            channel: GPIO channel that triggered the event
        """
        logger.info(f"Button pressed on channel {channel}")
        
        # Play feedback sound
        self.play_feedback_sound()
        
        # Start recording
        recorded_file = self.start_recording()
        
        if recorded_file:
            logger.info(f"Successfully recorded to {recorded_file}")
            # Here we would process the recording with APIs
            # This will be implemented in the next step
        
    def cleanup(self):
        """Clean up GPIO resources."""
        GPIO.cleanup()
        logger.info("GPIO resources cleaned up")

# Example usage
if __name__ == "__main__":
    try:
        # Import audio_utils if available
        try:
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from audio_utils import play_wav, record_audio
            
            class AudioUtils:
                @staticmethod
                def play_wav(file_path):
                    return play_wav(file_path)
                
                @staticmethod
                def record_audio(output_file=None, duration=5, device="hw:4,0"):
                    return record_audio(output_file, duration, device)
            
            audio_utils = AudioUtils()
            logger.info("Using audio_utils for playback and recording")
        except ImportError:
            audio_utils = None
            logger.warning("audio_utils not available, using fallback methods")
        
        # Create button handler
        handler = ButtonHandler(audio_utils)
        
        print("Button handler initialized. Press the button (GPIO 17) to start recording.")
        print("Press Ctrl+C to exit.")
        
        # Keep the program running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Clean up GPIO resources
        GPIO.cleanup()
