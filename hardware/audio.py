"""
Audio handling module for Polly.

This module provides functionality for audio recording and playback
using the USB audio adapter.
"""

import os
import time
import wave
import threading
import numpy as np
from datetime import datetime

try:
    import pyaudio
    import pygame
except ImportError:
    print("Warning: pyaudio or pygame not available. Using mock implementation.")
    
    # Mock PyAudio for development on systems without audio hardware
    class MockPyAudio:
        paInt16 = 16
        
        def __init__(self):
            print("Initialized MockPyAudio")
            
        def get_sample_size(self, format_type):
            return 2  # 16-bit audio
            
        def open(self, format, channels, rate, input, frames_per_buffer):
            print(f"Opening audio stream: format={format}, channels={channels}, rate={rate}, input={input}")
            return MockAudioStream()
            
        def terminate(self):
            print("PyAudio terminated")
    
    class MockAudioStream:
        def read(self, chunk_size):
            # Generate random audio data
            return bytes(np.random.randint(0, 255, chunk_size * 2, dtype=np.uint8))
            
        def stop_stream(self):
            print("Audio stream stopped")
            
        def close(self):
            print("Audio stream closed")
    
    # Use mock implementations if imports failed
    if 'pyaudio' not in globals():
        pyaudio = MockPyAudio
        
    if 'pygame' not in globals():
        class MockPygame:
            class mixer:
                @staticmethod
                def init(frequency=44100, size=-16, channels=2, buffer=4096):
                    print(f"Pygame mixer initialized: freq={frequency}, size={size}, channels={channels}")
                
                @staticmethod
                def quit():
                    print("Pygame mixer quit")
                    
                class Sound:
                    def __init__(self, file_path):
                        self.file_path = file_path
                        print(f"Loaded sound: {file_path}")
                        
                    def play(self):
                        print(f"Playing sound: {self.file_path}")
        
        pygame = MockPygame


class AudioRecorder:
    """Class to handle audio recording."""
    
    def __init__(self, 
                 format=pyaudio.paInt16,
                 channels=1,
                 rate=16000,
                 chunk_size=1024,
                 silence_threshold=1000,
                 silence_duration=2.0,
                 max_duration=30.0,
                 output_dir="audio"):
        """
        Initialize the audio recorder.
        
        Args:
            format: Audio format (default: 16-bit PCM)
            channels: Number of audio channels (default: 1 for mono)
            rate: Sampling rate in Hz (default: 16000)
            chunk_size: Number of frames per buffer (default: 1024)
            silence_threshold: Threshold for silence detection (default: 1000)
            silence_duration: Duration of silence to stop recording (default: 2.0 seconds)
            max_duration: Maximum recording duration (default: 30.0 seconds)
            output_dir: Directory to save recordings (default: "audio")
        """
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk_size = chunk_size
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_duration = max_duration
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        # Recording state
        self.is_recording = False
        self.recording_thread = None
        
    def _is_silent(self, data):
        """
        Check if the audio chunk is silent.
        
        Args:
            data: Audio data as bytes
            
        Returns:
            bool: True if the audio is below the silence threshold
        """
        # Convert bytes to numpy array
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Calculate RMS amplitude
        rms = np.sqrt(np.mean(np.square(audio_data)))
        return rms < self.silence_threshold
        
    def _record_audio(self, filename, callback=None):
        """
        Record audio until silence is detected or max duration is reached.
        
        Args:
            filename: Output filename
            callback: Function to call when recording is complete
        """
        # Open audio stream
        stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        print(f"Recording started: {filename}")
        
        frames = []
        silent_chunks = 0
        silent_threshold_chunks = int(self.silence_duration * self.rate / self.chunk_size)
        max_chunks = int(self.max_duration * self.rate / self.chunk_size)
        
        # Record until silence or max duration
        for i in range(max_chunks):
            if not self.is_recording:
                break
                
            data = stream.read(self.chunk_size)
            frames.append(data)
            
            # Check for silence
            if self._is_silent(data):
                silent_chunks += 1
                if silent_chunks >= silent_threshold_chunks:
                    print(f"Silence detected, stopping recording after {i} chunks")
                    break
            else:
                silent_chunks = 0
        
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        
        # Save the recording
        if frames:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
            
            print(f"Recording saved: {filename}")
            
            # Call the callback if provided
            if callback:
                callback(filename)
        else:
            print("No audio recorded")
            
        self.is_recording = False
        
    def start_recording(self, callback=None):
        """
        Start recording audio in a separate thread.
        
        Args:
            callback: Function to call when recording is complete
            
        Returns:
            str: Path to the output file
        """
        if self.is_recording:
            print("Already recording")
            return None
            
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"recording_{timestamp}.wav")
        
        # Start recording in a separate thread
        self.is_recording = True
        self.recording_thread = threading.Thread(
            target=self._record_audio,
            args=(filename, callback)
        )
        self.recording_thread.start()
        
        return filename
        
    def stop_recording(self):
        """Stop the current recording."""
        if self.is_recording:
            self.is_recording = False
            if self.recording_thread:
                self.recording_thread.join()
            print("Recording stopped")
            
    def cleanup(self):
        """Clean up audio resources."""
        self.stop_recording()
        self.audio.terminate()
        print("Audio recorder cleaned up")


class AudioPlayer:
    """Class to handle audio playback."""
    
    def __init__(self, responses_dir="audio/responses"):
        """
        Initialize the audio player.
        
        Args:
            responses_dir: Directory containing response audio files
        """
        self.responses_dir = responses_dir
        
        # Create responses directory if it doesn't exist
        os.makedirs(responses_dir, exist_ok=True)
        
        # Initialize pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        
        # Load immediate response sounds
        self.immediate_responses = self._load_immediate_responses()
        
    def _load_immediate_responses(self):
        """
        Load immediate response sounds from the responses directory.
        
        Returns:
            dict: Dictionary of response sounds
        """
        responses = {}
        
        # Check if responses directory exists and has files
        if os.path.exists(self.responses_dir):
            for filename in os.listdir(self.responses_dir):
                if filename.endswith(".wav") and filename.startswith("immediate_"):
                    path = os.path.join(self.responses_dir, filename)
                    name = filename.replace("immediate_", "").replace(".wav", "")
                    try:
                        responses[name] = pygame.mixer.Sound(path)
                        print(f"Loaded response sound: {name}")
                    except Exception as e:
                        print(f"Error loading sound {path}: {e}")
        
        # If no responses found, create a default one
        if not responses:
            print("No immediate response sounds found")
        
        return responses
        
    def play_immediate_response(self, name=None):
        """
        Play an immediate response sound.
        
        Args:
            name: Name of the response to play (random if None)
            
        Returns:
            bool: True if sound was played, False otherwise
        """
        if not self.immediate_responses:
            print("No immediate responses available")
            return False
            
        # Select a response
        if name is None or name not in self.immediate_responses:
            # Choose random response
            if self.immediate_responses:
                name = np.random.choice(list(self.immediate_responses.keys()))
            else:
                return False
                
        # Play the response
        try:
            self.immediate_responses[name].play()
            print(f"Playing immediate response: {name}")
            return True
        except Exception as e:
            print(f"Error playing sound: {e}")
            return False
            
    def play_audio_file(self, file_path):
        """
        Play an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            bool: True if sound was played, False otherwise
        """
        if not os.path.exists(file_path):
            print(f"Audio file not found: {file_path}")
            return False
            
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.play()
            print(f"Playing audio file: {file_path}")
            return True
        except Exception as e:
            print(f"Error playing audio file: {e}")
            return False
            
    def cleanup(self):
        """Clean up audio player resources."""
        pygame.mixer.quit()
        print("Audio player cleaned up")


# Example usage
if __name__ == "__main__":
    # Create recorder and player
    recorder = AudioRecorder(output_dir="audio")
    player = AudioPlayer(responses_dir="audio/responses")
    
    try:
        # Play an immediate response
        player.play_immediate_response()
        
        # Record audio
        def recording_callback(filename):
            print(f"Recording complete: {filename}")
            # Play back the recording
            time.sleep(1)  # Wait a bit before playback
            player.play_audio_file(filename)
            
        filename = recorder.start_recording(callback=recording_callback)
        
        # Wait for recording to complete
        while recorder.is_recording:
            time.sleep(0.1)
            
        print("Example complete")
        
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        # Clean up resources
        recorder.cleanup()
        player.cleanup()
