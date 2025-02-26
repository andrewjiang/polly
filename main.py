#!/usr/bin/env python3
"""
Polly - AI-Powered Talking Bird

Main entry point for the Polly application.
"""

import os
import time
import threading
import argparse
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import hardware modules
try:
    from hardware.button import Button
    from hardware.audio import AudioRecorder, AudioPlayer
except ImportError as e:
    logger.error(f"Error importing hardware modules: {e}")
    logger.warning("Running in mock mode without hardware support")
    
    # Mock implementations for development without hardware
    class MockButton:
        def __init__(self, pin=17, callback=None, bouncetime=200):
            self.pin = pin
            self.callback = callback
            
        def setup(self):
            logger.info(f"Mock button setup on pin {self.pin}")
            
        def start_detection(self, callback=None):
            cb = callback if callback is not None else self.callback
            logger.info(f"Mock button detection started on pin {self.pin}")
            
        def cleanup(self):
            logger.info("Mock button cleanup")
    
    class MockAudioRecorder:
        def __init__(self, **kwargs):
            self.is_recording = False
            
        def start_recording(self, callback=None):
            self.is_recording = True
            logger.info("Mock recording started")
            
            # Simulate recording for 3 seconds
            def simulate_recording():
                time.sleep(3)
                self.is_recording = False
                if callback:
                    callback("audio/mock_recording.wav")
                    
            threading.Thread(target=simulate_recording).start()
            return "audio/mock_recording.wav"
            
        def stop_recording(self):
            self.is_recording = False
            logger.info("Mock recording stopped")
            
        def cleanup(self):
            logger.info("Mock audio recorder cleanup")
    
    class MockAudioPlayer:
        def __init__(self, responses_dir="audio/responses"):
            self.responses_dir = responses_dir
            
        def play_immediate_response(self, name=None):
            logger.info(f"Mock playing immediate response: {name}")
            return True
            
        def play_audio_file(self, file_path):
            logger.info(f"Mock playing audio file: {file_path}")
            return True
            
        def cleanup(self):
            logger.info("Mock audio player cleanup")
    
    # Replace hardware modules with mock implementations
    Button = MockButton
    AudioRecorder = MockAudioRecorder
    AudioPlayer = MockAudioPlayer

# Import server module
try:
    from server.websocket_server import WebSocketServer
except ImportError as e:
    logger.error(f"Error importing server module: {e}")
    
    # Mock WebSocketServer for development
    class MockWebSocketServer:
        def __init__(self, host="0.0.0.0", port=8765):
            self.host = host
            self.port = port
            
        def start_server(self, audio_callback=None, response_callback=None):
            logger.info(f"Mock WebSocket server started on {self.host}:{self.port}")
            
        def stop(self):
            logger.info("Mock WebSocket server stopped")
            
        async def send_audio(self, audio_file):
            logger.info(f"Mock sending audio: {audio_file}")
            return True
    
    # Replace server module with mock implementation
    WebSocketServer = MockWebSocketServer


class PollyApp:
    """Main application class for Polly."""
    
    def __init__(self, host="0.0.0.0", port=8765, button_pin=17):
        """
        Initialize the Polly application.
        
        Args:
            host: Host to bind the WebSocket server to
            port: Port to bind the WebSocket server to
            button_pin: GPIO pin for the button
        """
        self.host = host
        self.port = port
        self.button_pin = button_pin
        
        # Create components
        self.button = Button(pin=button_pin, callback=self.on_button_press)
        self.audio_recorder = AudioRecorder(output_dir="audio")
        self.audio_player = AudioPlayer(responses_dir="audio/responses")
        self.websocket_server = WebSocketServer(host=host, port=port)
        
        # State
        self.is_running = False
        self.server_thread = None
        
    def on_button_press(self, channel):
        """
        Handle button press event.
        
        Args:
            channel: GPIO channel
        """
        logger.info(f"Button pressed on channel {channel}")
        
        # Play immediate response
        self.audio_player.play_immediate_response()
        
        # Start recording
        filename = self.audio_recorder.start_recording(callback=self.on_recording_complete)
        logger.info(f"Recording to {filename}")
        
    def on_recording_complete(self, filename):
        """
        Handle recording complete event.
        
        Args:
            filename: Path to the recorded audio file
        """
        logger.info(f"Recording complete: {filename}")
        
        # Send audio to web app
        asyncio.run(self.send_audio_to_webapp(filename))
        
    async def send_audio_to_webapp(self, filename):
        """
        Send audio to web app.
        
        Args:
            filename: Path to the audio file
        """
        logger.info(f"Sending audio to web app: {filename}")
        
        # Send audio via WebSocket
        await self.websocket_server.send_audio(filename)
        
    def on_response_received(self, filename):
        """
        Handle response received event.
        
        Args:
            filename: Path to the response audio file
        """
        logger.info(f"Response received: {filename}")
        
        # Play response
        self.audio_player.play_audio_file(filename)
        
    def start(self):
        """Start the Polly application."""
        if self.is_running:
            logger.warning("Polly is already running")
            return
            
        logger.info("Starting Polly")
        
        # Set up button
        self.button.setup()
        self.button.start_detection()
        
        # Start WebSocket server in a separate thread
        self.server_thread = threading.Thread(
            target=self.websocket_server.start_server,
            kwargs={
                "response_callback": self.on_response_received
            }
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        
        self.is_running = True
        logger.info("Polly started")
        
        # Create sample immediate response if none exist
        self._create_sample_responses()
        
    def stop(self):
        """Stop the Polly application."""
        if not self.is_running:
            logger.warning("Polly is not running")
            return
            
        logger.info("Stopping Polly")
        
        # Stop recording if in progress
        self.audio_recorder.stop_recording()
        
        # Stop WebSocket server
        self.websocket_server.stop()
        
        # Clean up resources
        self.button.cleanup()
        self.audio_recorder.cleanup()
        self.audio_player.cleanup()
        
        self.is_running = False
        logger.info("Polly stopped")
        
    def _create_sample_responses(self):
        """Create sample immediate response sounds if none exist."""
        responses_dir = "audio/responses"
        os.makedirs(responses_dir, exist_ok=True)
        
        # Check if any immediate response files exist
        has_responses = False
        for filename in os.listdir(responses_dir):
            if filename.startswith("immediate_") and filename.endswith(".wav"):
                has_responses = True
                break
                
        # If no responses exist, create a README file with instructions
        if not has_responses:
            readme_path = os.path.join(responses_dir, "README.md")
            with open(readme_path, "w") as f:
                f.write("""# Immediate Response Sounds

This directory should contain immediate response sounds that Polly will play
when the button is pressed, before recording starts.

Files should be named with the format `immediate_NAME.wav`, where NAME is a
descriptive name for the response.

Example files:
- `immediate_thinking.wav` - "Let me think about that..."
- `immediate_listening.wav` - "I'm listening..."
- `immediate_processing.wav` - "Processing your question..."

You can create these files using text-to-speech services or record them yourself.
""")
            logger.info(f"Created {readme_path} with instructions for immediate responses")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Polly - AI-Powered Talking Bird")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the WebSocket server to")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind the WebSocket server to")
    parser.add_argument("--button-pin", type=int, default=17, help="GPIO pin for the button")
    return parser.parse_args()


def main():
    """Main entry point."""
    # Parse command line arguments
    args = parse_args()
    
    # Create and start the application
    app = PollyApp(
        host=args.host,
        port=args.port,
        button_pin=args.button_pin
    )
    
    try:
        # Start the application
        app.start()
        
        # Keep the main thread running
        logger.info("Polly is running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        # Stop the application
        app.stop()


if __name__ == "__main__":
    main()
