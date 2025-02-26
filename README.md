# Polly - AI-Powered Talking Bird

Polly is a stuffed bird with an embedded Raspberry Pi 4 that enables natural voice interaction for children. It listens, responds intelligently using ChatGPT, and provides an engaging, interactive experience.

## Overview

Polly is activated via a hidden push button in its wing and records speech until 2 seconds of silence. It then sends the recorded speech to a connected smartphone via Wi-Fi, where the phone processes the audio, generates a ChatGPT-powered response, and sends back Polly's reply using text-to-speech.

## Repository Structure

```
polly/
├── hardware/           # GPIO and audio handling scripts
├── server/             # WebSocket server for Pi-to-phone communication
├── web_app/            # Web interface for iPhone
├── audio/              # Pre-recorded response sounds
│   └── responses/      # Directory for response audio files
├── tests/              # Unit and integration tests
├── docs/               # Developer documentation
├── main.py             # Main entry point for the application
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── PRD.md              # Product Requirements Document
└── SPECS.md            # Technical Specifications
```

## Hardware Requirements

- Raspberry Pi 4 Model B (4GB) - CanaKit Starter PRO Kit
- 3.5mm Lavalier Mic (via Plugable USB Audio Adapter)
- HONKYOB USB Mini Speaker (USB-powered)
- Lilypad Momentary Push Button (Hidden inside the wing, connected to GPIO 17)
- 5V 3A Power Supply (from CanaKit) / USB Power Bank for portability
- Wi-Fi connectivity (connecting to phone hotspot)

## Software Components

### Raspberry Pi
- Python scripts for hardware interaction (button, audio)
- WebSocket server for communication with the web app
- Audio recording and playback functionality

### Web App (iPhone)
- Simple web interface for processing audio
- Integration with OpenAI APIs (Whisper for STT, ChatGPT for responses)
- Text-to-Speech conversion
- WebSocket client for communication with the Pi

## Setup Instructions

### Raspberry Pi Setup
1. Install Raspberry Pi OS on the microSD card
2. Configure the USB sound adapter for both microphone and speaker
3. Install required dependencies:
   ```bash
   sudo apt-get install python3-pyaudio python3-pygame
   pip install websockets RPi.GPIO
   ```
4. Clone this repository and install Python dependencies:
   ```bash
   git clone https://github.com/yourusername/polly.git
   cd polly
   pip install -r requirements.txt
   ```
5. Run the main application:
   ```bash
   python main.py
   ```

### Web App Setup
1. Host the web app files on a local or cloud server
2. Access the web app from an iPhone
3. Connect to the Raspberry Pi's WebSocket server
4. Configure OpenAI API keys in the web app

## User Flow
1. User presses the button (hidden in Polly's wing)
2. Polly starts listening and records the child's speech
3. Polly sends the recording to the connected phone via Wi-Fi
4. The phone web app processes the audio and generates a response
5. The phone sends the synthesized audio back to Polly
6. Polly plays the response using its USB-powered speaker

## Development

### Prerequisites
- Python 3.7+
- Node.js (for web development)
- OpenAI API keys
- Raspberry Pi hardware setup

### Running Tests
```bash
# Run unit tests
python -m unittest discover tests
```

## License
[MIT License](LICENSE)

## Acknowledgements
- OpenAI for ChatGPT and Whisper APIs
- Raspberry Pi Foundation
