# Polly AI-Powered Stuffed Bird – Technical Specifications

## 1. Programming Stack

- **Primary Language – Python:** Officially recommended for Raspberry Pi, beginner-friendly, and well-supported.
- **Frontend – Web App:** Simple web interface for iPhone to process audio and generate responses.
- **Backend – Python Server on Pi:** Handles audio recording and playback, communicates with the web app.
- **Key Libraries:**
  - `RPi.GPIO` – Button handling on GPIO 17
  - `pyaudio` – Audio capture via USB audio adapter
  - `pygame` – Audio playback
  - `websockets` – Real-time communication between Pi and web app
- **AI Services (on Web App):**
  - **ChatGPT API (OpenAI):** Conversational response generation
  - **Whisper API (OpenAI):** Speech-to-text transcription
  - **Text-to-Speech (TTS):** AWS Polly, Google TTS, or browser TTS for voice playback

## 2. Repository Structure

```plaintext
polly-project/
├── hardware/           # GPIO and audio handling scripts
├── server/             # WebSocket server for Pi-to-phone communication
├── web_app/            # Web interface for iPhone
├── audio/              # Pre-recorded response sounds
├── tests/              # Unit and integration tests
└── docs/               # Developer documentation
```

## 3. Deployment Strategy

- **Raspberry Pi:** Runs Python server for hardware interaction and audio handling
- **Web App:** Hosted static site that connects to Pi via WebSockets
- **Device Workflow:**
  - User presses button on GPIO 17 → Polly plays immediate response → Records audio → Sends audio to web app → Web app processes with AI → Sends response back → Polly plays response
- **Internet Connectivity:** Required for web app to access OpenAI APIs
- **Autostart on Boot:** Uses systemd to ensure the Pi software runs automatically
- **Security Considerations:** Local network communication only (phone hotspot)

## 4. Testing & CI/CD

- **Unit Testing:** Covers hardware abstraction, audio handling, and communication
- **Integration Testing:** Simulates full interaction (button press → record → web app processing → playback)
- **Manual Testing:** Regular testing with actual hardware setup

## 5. Communication Design

### **WebSocket Communication:**
- Real-time bidirectional communication between Pi and web app
- Pi sends audio recordings to web app
- Web app sends processed responses back to Pi

### **Example WebSocket Flow:**
```python
# Pi side
import asyncio
import websockets
import json

async def send_audio(websocket, audio_data):
    await websocket.send(json.dumps({
        "type": "audio",
        "data": audio_data
    }))
    
    response = await websocket.recv()
    return json.loads(response)
```

## 6. Version Control & Collaboration

- **Simple branching strategy:**
  - `main` – Stable production code
  - `feature/*` – New features
- **Pull Requests & Code Reviews:** Every feature merged via PR

## 7. Best Practice Development Flow

- **Iterative Development:** Develop and test in small steps
- **Modular Design:** Separate hardware, communication, and web app
- **Regular Testing:** Test with actual hardware frequently
- **Documentation:** Keep documentation up-to-date

## 8. Nice-to-Haves (Optional Enhancements)

- **Web Dashboard:** Enhanced interface for customization and debugging
- **Wake-Word Detection:** Enable Polly to respond to a keyword without pressing a button
- **Offline Mode:** Store limited responses locally for when there's no internet
- **Battery Operation & Power Management:** Improve power efficiency for portability
- **Multi-language Support:** Expand beyond English responses

## Initial Setup Guide

1. **Prepare Raspberry Pi:** Install Raspberry Pi OS, enable SSH, and set up Wi-Fi.
2. **System Configuration:** Install dependencies:
   ```bash
   sudo apt-get install python3-pyaudio python3-pygame
   pip install websockets RPi.GPIO
   ```
3. **Clone Repository & Install Dependencies:**
   ```bash
   git clone https://github.com/yourusername/polly-project.git
   cd polly-project
   pip install -r requirements.txt
   ```
4. **Test Button Press Handling:**
   ```python
   import RPi.GPIO as GPIO
   BUTTON_PIN = 17  # Using GPIO 17 as specified
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
   def on_button_press(channel):
       print("Button Pressed!")
   GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=on_button_press, bouncetime=200)
   ```
5. **Test Audio Recording:**
   ```python
   import pyaudio
   import wave
   def record_audio(filename: str, duration: int = 5):
       p = pyaudio.PyAudio()
       stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
       frames = [stream.read(1024) for _ in range(int(16000 / 1024 * duration))]
       stream.stop_stream()
       stream.close()
       p.terminate()
       with wave.open(filename, 'wb') as wf:
           wf.setnchannels(1)
           wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
           wf.setframerate(16000)
           wf.writeframes(b''.join(frames))
   ```
6. **Start WebSocket Server on Pi:**
   ```python
   import asyncio
   import websockets

   async def handle_client(websocket, path):
       # Handle communication with web app
       pass

   start_server = websockets.serve(handle_client, "0.0.0.0", 8765)
   asyncio.get_event_loop().run_until_complete(start_server)
   asyncio.get_event_loop().run_forever()
   ```
7. **Create Simple Web App:**
   - HTML/CSS/JavaScript interface
   - WebSocket connection to Pi
   - Integration with OpenAI APIs

This technical specification provides a detailed guide for Polly's development, focusing on a web app interface for the iPhone that communicates with the Raspberry Pi via WebSockets.
