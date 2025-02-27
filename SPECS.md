# Polly AI-Powered Stuffed Bird – Technical Specifications

## 1. Programming Stack

- **Primary Language – Python:** Officially recommended for Raspberry Pi, beginner-friendly, and well-supported.
- **Backend – Python on Pi:** Handles all functionality including audio recording/playback and API communication.
- **Key Libraries:**
  - `RPi.GPIO` – Button handling on GPIO 17
  - `subprocess` – Audio recording and playback via system commands
  - `pygame` – Alternative audio playback method
  - `requests` – API communication with OpenAI and Eleven Labs
  - `openai` – Official OpenAI Python client
- **AI Services (Direct API Access):**
  - **ChatGPT API (OpenAI):** Conversational response generation
  - **Whisper API (OpenAI):** Speech-to-text transcription
  - **Text-to-Speech (TTS):** Eleven Labs or similar for voice synthesis

## 2. Repository Structure

```plaintext
polly-project/
├── hardware/           # GPIO and audio handling scripts
├── api/                # API integration for OpenAI and TTS services
├── audio/              # Recorded audio and pre-recorded responses
│   └── responses/      # Pre-recorded response sounds (beep.wav, hello.mp3)
├── tests/              # Unit and integration tests
├── docs/               # Developer documentation
├── audio_utils.py      # Audio utility functions for playback and recording
├── functionality_test.py # Test script for audio functionality
├── main.py             # Main application entry point
└── config.py           # Configuration settings and API keys
```

## 3. Hardware Component Mapping

### GPIO Pins
| Component | GPIO Pin | Purpose |
|-----------|----------|---------|
| Push Button | GPIO 17 | Activates Polly to start listening |
| LED Indicator (future) | GPIO 18 | Visual feedback for listening/processing status |

### Audio Devices
| Device | ALSA ID | Purpose | Connected Component |
|--------|---------|---------|---------------------|
| Headphone Jack | hw:2,0 | Audio playback | USB Mini Speaker |
| USB Audio Input | hw:4,0 | Audio recording | 3.5mm Lavalier Microphone |
| Alternative Recording | hw:3,0 | Backup recording device | (Optional) |

### USB Ports
| Port | Connected Device | Purpose |
|------|-----------------|---------|
| USB 1 | USB Mini Speaker | Audio playback |
| USB 2 | USB Audio Adapter | Microphone input |
| USB 3 | (Available) | Future expansion |
| USB 4 | (Available) | Future expansion |

### Network Interfaces
| Interface | Purpose |
|-----------|---------|
| Wi-Fi (wlan0) | Connection to internet for API access |
| Ethernet (eth0) | (Optional) Development and debugging |

## 4. Audio System Specifications

### Audio Device Configuration
- **Headphone Jack:** `hw:2,0` (Raspberry Pi onboard audio)
- **USB Audio Input:** `hw:4,0` (USB audio adapter for microphone)
- **Alternative Recording Device:** `hw:3,0` (Secondary option)

### Audio Playback
- **WAV Playback:** Using `aplay` system command
  ```python
  subprocess.run(["aplay", wav_file], check=True)
  ```
- **MP3 Playback:** Using `mpg123` system command with device specification
  ```python
  subprocess.run(["mpg123", "-a", device, mp3_file], check=True)
  ```
- **Volume Control:** Set to maximum before playback
  ```python
  subprocess.run(["amixer", "-c", "2", "set", "PCM", "100%"], check=False)
  ```

### Audio Recording
- **Recording Command:** Using `arecord` system command
  ```python
  subprocess.run([
      "arecord", 
      "-D", device,
      "-d", str(duration),
      "-f", "cd",  # CD quality (16-bit, 44100Hz, stereo)
      "-t", "wav", 
      output_file
  ], check=True)
  ```
- **Recommended Format:** 16-bit, 16kHz mono for speech recording
- **Silence Detection:** Stop recording after 2 seconds of silence

## 5. API Integration

### OpenAI Whisper (Speech-to-Text)
```python
import openai

def transcribe_audio(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file
        )
    return transcript["text"]
```

### OpenAI ChatGPT (Conversation)
```python
import openai

def get_chatgpt_response(prompt, conversation_history=None):
    if conversation_history is None:
        conversation_history = []
    
    messages = [
        {"role": "system", "content": "You are Polly, a friendly talking bird who loves to chat with children."},
    ] + conversation_history + [
        {"role": "user", "content": prompt}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        temperature=0.7
    )
    
    return response.choices[0].message["content"]
```

### Eleven Labs (Text-to-Speech)
```python
import requests

def generate_speech(text, voice_id="default"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": "YOUR_API_KEY"
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        output_path = f"audio/responses/response_{int(time.time())}.mp3"
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path
    else:
        print(f"Error: {response.status_code}")
        return None
```

## 6. Deployment Strategy

- **Raspberry Pi:** Runs all software components including audio handling and API communication
- **Device Workflow:**
  - User presses button on GPIO 17 → Polly plays immediate response → Records audio → Processes with APIs → Plays response
- **Internet Connectivity:** Required for API access (OpenAI and Eleven Labs)
- **Autostart on Boot:** Uses systemd to ensure the Pi software runs automatically
- **Security Considerations:** Secure storage of API keys in configuration file

## 7. Testing & CI/CD

- **Unit Testing:** Covers hardware abstraction, audio handling, and API communication
- **Integration Testing:** Simulates full interaction (button press → record → API processing → playback)
- **Manual Testing:** Regular testing with actual hardware setup
- **Audio Testing:** Dedicated test script (`functionality_test.py`) for audio functionality

## 8. Error Handling & Recovery

- **Network Issues:** Fallback to pre-recorded responses if API calls fail
- **Audio Device Errors:** Automatic retry with alternative devices
- **API Rate Limiting:** Implement backoff strategy for API calls
- **Power Loss:** Save state periodically to recover after unexpected shutdown

## 9. Best Practice Development Flow

- **Iterative Development:** Develop and test in small steps
- **Modular Design:** Separate hardware, API communication, and audio processing
- **Regular Testing:** Test with actual hardware frequently
- **Documentation:** Keep documentation up-to-date

## 10. Nice-to-Haves (Optional Enhancements)

- **Wake-Word Detection:** Enable Polly to respond to a keyword without pressing a button
- **Offline Mode:** Store limited responses locally for when there's no internet
- **Battery Operation & Power Management:** Improve power efficiency for portability
- **Multi-language Support:** Expand beyond English responses
- **Web Dashboard:** Future enhancement for configuration and monitoring

## 11. Audio Utility Library (`audio_utils.py`)

The `audio_utils.py` module provides the following functions:

- **`play_wav(wav_file, device)`**: Plays a WAV file using `aplay`
- **`play_mp3(mp3_file, device)`**: Plays an MP3 file using `mpg123`
- **`play_audio_file(audio_file, device)`**: Automatically detects file format and plays it
- **`record_audio(output_file, duration, device)`**: Records audio using `arecord`
- **`play_pygame(audio_file)`**: Alternative playback using the `pygame` library

## Initial Setup Guide

1. **Prepare Raspberry Pi:** Install Raspberry Pi OS, enable SSH, and set up Wi-Fi.
2. **System Configuration:** Install dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip python3-pygame mpg123 alsa-utils
   pip3 install openai requests RPi.GPIO
   ```
3. **Clone Repository & Install Dependencies:**
   ```bash
   git clone https://github.com/yourusername/polly-project.git
   cd polly-project
   pip3 install -r requirements.txt
   ```
4. **Configure API Keys:**
   ```python
   # config.py
   OPENAI_API_KEY = "your_openai_api_key"
   ELEVEN_LABS_API_KEY = "your_eleven_labs_api_key"
   ```
5. **Test Button Press Handling:**
   ```python
   import RPi.GPIO as GPIO
   BUTTON_PIN = 17  # Using GPIO 17 as specified
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
   def on_button_press(channel):
       print("Button Pressed!")
   GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=on_button_press, bouncetime=200)
   ```
6. **Test Audio Playback and Recording:**
   ```bash
   # Run the functionality test script
   python3 functionality_test.py --test all
   ```
7. **Test API Integration:**
   ```bash
   # Test OpenAI and Eleven Labs integration
   python3 api_test.py
   ```

This technical specification provides a detailed guide for Polly's development, focusing on direct API integration from the Raspberry Pi for a standalone, responsive experience.
