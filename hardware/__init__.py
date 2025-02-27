"""
Hardware module for Polly.

This package contains modules for interacting with hardware components:
- button.py: Button press detection and handling
- audio.py: Audio recording and playback functionality
"""

from hardware.button import ButtonHandler
from hardware.audio import AudioRecorder, AudioPlayer

__all__ = ['ButtonHandler', 'AudioRecorder', 'AudioPlayer']
