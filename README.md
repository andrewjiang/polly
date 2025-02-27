# Polly - Voice Assistant

Polly is a voice assistant that processes speech and generate responses. It's designed to run on a Raspberry Pi with a button and microphone.

## Features

- Button-triggered audio recording
- WebSocket communication with a web app for audio processing
- Audio playback of responses
- Configurable settings via environment variables or command line arguments
- Health monitoring of system components
- Structured logging with operation tracking
- Graceful error handling and recovery
- Mock implementations for development without hardware

## Hardware Requirements

- Raspberry Pi (tested on Raspberry Pi 4)
- USB microphone or USB audio interface
- Speaker connected to the headphone jack or USB audio interface
- Push button connected to GPIO pin 17
- LED connected to GPIO pin 27 (optional)

## Software Requirements

- Raspberry Pi OS (Bullseye or newer)
- Python 3.7+
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/polly.git
   cd polly
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration (optional):
   ```
   POLLY_HOST=localhost
   POLLY_PORT=8765
   POLLY_BUTTON_PIN=17
   POLLY_RECORDING_TIME=5
   ```

## Usage

### Basic Usage

Run Polly with default settings:

```
python main.py
```

### Command Line Options

```
python main.py --host localhost --port 8765 --button-pin 17 --debug
```

Available options:
- `--host`: WebSocket server host (default: localhost)
- `--port`: WebSocket server port (default: 8765)
- `--button-pin`: GPIO pin for the button (default: 17)
- `--debug`: Enable debug logging

### Environment Variables

All settings can be configured via environment variables:

- `POLLY_HOST`: WebSocket server host
- `POLLY_PORT`: WebSocket server port
- `POLLY_BUTTON_PIN`: GPIO pin for the button
- `POLLY_AUDIO_CHANNELS`: Number of audio channels
- `POLLY_AUDIO_RATE`: Audio sample rate
- `POLLY_AUDIO_CHUNK`: Audio chunk size
- `POLLY_RECORDING_TIME`: Recording duration in seconds
- `POLLY_SOUNDS_DIR`: Directory for sound files
- `POLLY_STATUS_FILE`: Path to status file
- `POLLY_LOG_FILE`: Path to log file
- `POLLY_LOG_LEVEL`: Logging level

## Project Structure

- `main.py`: Main application entry point
- `config.py`: Configuration management
- `utils/`: Utility modules
  - `logging_utils.py`: Enhanced logging functionality
  - `health_monitor.py`: System health monitoring
- `sounds/`: Directory for sound files
  - `start_recording.wav`: Sound played when recording starts
  - `stop_recording.wav`: Sound played when recording stops

## Development

### Running Without Hardware

The application includes mock implementations for hardware components, allowing development and testing without a Raspberry Pi, button, or audio devices.

### Adding Custom Sounds

Place WAV files in the `sounds` directory:
- `start_recording.wav`: Played when recording starts
- `stop_recording.wav`: Played when recording stops

## Health Monitoring

The application includes a health monitoring system that tracks the status of various components. The status is saved to a JSON file (`polly_status.json` by default) and can be used to monitor the application's health.

## Logging

Logs are written to both the console and a log file (`polly.log` by default). The logging level can be configured via the `POLLY_LOG_LEVEL` environment variable or the `--debug` command line option.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for Whisper and ChatGPT APIs
- Eleven Labs for text-to-speech API
- The Raspberry Pi community
