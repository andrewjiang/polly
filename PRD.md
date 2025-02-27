# **Product Requirements Document (PRD) – Polly the ChatGPT-Powered Talking Bird**

## **1. Product Overview**
Polly is a stuffed bird with an embedded Raspberry Pi 4 that enables natural voice interaction for children. It listens, responds intelligently using ChatGPT, and provides an engaging, interactive experience. Polly is activated via a hidden push button in its wing and records speech until 2 seconds of silence. It then processes the recorded speech directly on the Raspberry Pi, sending it to OpenAI's Whisper for transcription and ChatGPT for generating a response. The response is converted to speech using Eleven Labs or similar TTS service and played back through Polly's speaker.

## **2. Key Features & Functional Requirements**
### **Core Features (MVP)**
✅ **Embedded Electronics:** Electronics are housed in a removable module for easy maintenance.  
✅ **Voice Activation:** Push button inside the wing activates Polly. Future versions may add a wake word.  
✅ **Speech Processing:**
   - Polly records audio until 2 seconds of silence.
   - Background noise filtering ensures clear speech capture.
✅ **ChatGPT Integration:**  
   - Polly directly sends recorded audio to OpenAI Whisper API for transcription.  
   - The transcribed text is sent to ChatGPT API to generate a response.  
   - The response is converted to speech using Eleven Labs or similar TTS service.  
✅ **Text-to-Speech Response:**  
   - The response is played back via Polly's **USB-powered mini speaker**.  
   - A simple immediate audio response plays on the Pi for responsiveness while waiting for the full response.
✅ **Randomized Responses:** Polly introduces variation in its responses to feel more natural.  
✅ **Uncertainty Handling:** If Polly doesn't understand, it says: *"I'm not sure, can you ask again?"* with random variations.  
✅ **Basic Power Management:** Polly enters sleep mode when inactive, waking only when the button is pressed.  

### **"Nice-to-Haves" (Future Enhancements)**
⭐ **Wake Word Activation (e.g., "Hey Polly")** instead of button press.  
⭐ **Offline Mode with Preloaded Responses** for times when Polly has no internet connection.  
⭐ **Low Battery Alert** ("I'm feeling sleepy, charge me soon!").  
⭐ **Facial Expressions or LED Indicator** to show listening/thinking status.  
⭐ **Customizable Personality Modes** (e.g., funny Polly, serious Polly, storytelling mode).  
⭐ **Web App Interface** for configuration, monitoring, and enhanced features.

## **3. Hardware Requirements (Updated for Your Order)**
| Component         | Model / Details |
|------------------|----------------|
| **Main Board**   | Raspberry Pi 4 Model B (4GB) - CanaKit Starter PRO Kit |
| **Microphone**   | **3.5mm Lavalier Mic (via Plugable USB Audio Adapter)** |
| **Speaker**      | **HONKYOB USB Mini Speaker** (USB-powered) |
| **Push Button**  | **Lilypad Momentary Push Button** (Hidden inside the wing, connected to GPIO 17) |
| **Power Supply** | 5V 3A (from CanaKit) / USB Power Bank for portability |
| **Connectivity** | Wi-Fi (connecting to home network or phone hotspot) |

## **4. Software Requirements (Updated for Direct API Approach)**
| Component | Tool / Library |
|-----------|---------------|
| **Voice Activation (Button)** | Python script detecting GPIO 17 button press |
| **Audio Capture & Processing** | `subprocess` (arecord) + Silence detection via **USB sound card** |
| **Speech-to-Text (STT)** | OpenAI Whisper API (direct from Raspberry Pi) |
| **AI Response** | OpenAI ChatGPT API (direct from Raspberry Pi) |
| **Text-to-Speech (TTS)** | Eleven Labs API or similar (direct from Raspberry Pi) |
| **Audio Playback** | `subprocess` (aplay/mpg123) through headphone jack |

## **5. User Flow (Updated for Direct API Approach)**
1. **User presses the button (hidden in Polly's wing, connected to GPIO 17).**  
2. **Polly starts listening and records the child's speech.**  
   - Polly stops recording when it detects 2 seconds of silence.  
   - **Audio is captured via the 3.5mm microphone connected to the USB sound card.**
   - Background noise is filtered for clarity.  
   - Polly plays a simple immediate response for responsiveness.
3. **Polly processes the recording directly:**  
   - Sends the audio to OpenAI Whisper API for transcription.  
   - Sends the transcribed text to ChatGPT API to generate a response.  
   - Sends the response text to Eleven Labs API for text-to-speech conversion.  
4. **Polly plays the synthesized audio response using its USB-powered speaker.**  
5. **Polly goes into sleep mode until the button is pressed again.**  

---

## **🔄 Implementation Plan (Direct API Approach)**

### **Phase 1: Core Functionality**
- [x] **Audio System**
  - [x] Configure USB audio devices
  - [x] Implement audio playback (WAV/MP3)
  - [x] Implement audio recording with silence detection
- [ ] **Button Integration**
  - [x] Test button press detection
  - [ ] Integrate button with recording system
  - [ ] Add immediate audio feedback on press
- [ ] **API Integration**
  - [ ] Set up OpenAI API access (Whisper + ChatGPT)
  - [ ] Implement audio transcription with Whisper
  - [ ] Implement conversation handling with ChatGPT
  - [ ] Set up Eleven Labs or similar TTS service
  - [ ] Implement response synthesis and playback
- [ ] **End-to-End Testing**
  - [ ] Test full interaction flow
  - [ ] Optimize response time
  - [ ] Handle error cases gracefully

### **Phase 2: Refinement & Enhancements**
- [ ] **Conversation Management**
  - [ ] Implement conversation history/context
  - [ ] Add personality customization
  - [ ] Improve response quality and relevance
- [ ] **System Reliability**
  - [ ] Add error recovery mechanisms
  - [ ] Implement offline fallback responses
  - [ ] Optimize battery usage
- [ ] **User Experience**
  - [ ] Add LED indicators for system status
  - [ ] Improve audio quality and responsiveness
  - [ ] Implement volume control

### **Phase 3: Optional Web App (Future)**
- [ ] **Web Interface**
  - [ ] Create configuration dashboard
  - [ ] Implement usage monitoring
  - [ ] Add conversation history viewing
- [ ] **Enhanced Features**
  - [ ] Remote control and monitoring
  - [ ] Voice customization
  - [ ] Content filtering and parental controls

---

## **Audio System Learnings**
- **WAV Playback:** Works best with simplified `aplay` command without specifying device
- **MP3 Playback:** Works well with `mpg123 -a hw:2,0` (specifying headphone jack)
- **Volume Control:** Set to maximum with `amixer -c 2 set PCM 100%`
- **Recording:** Works with `arecord -D hw:4,0` (USB audio device)
- **Audio Formats:** 16-bit, 16kHz mono works well for speech recording
- **Device Mapping:**
  - Headphone jack: hw:2,0
  - USB audio input: hw:4,0
  - Alternative recording device: hw:3,0

---

## **Direct API Approach Benefits**
- **Simplified Architecture:** No need for a separate web app, reducing complexity
- **Reduced Latency:** Eliminates one communication hop, making responses faster
- **Standalone Operation:** Polly functions independently without requiring a phone
- **Easier Development:** Only need to develop one codebase (Python on the Pi)
- **Fewer Potential Points of Failure:** Removes WebSocket communication issues

---

Your PRD is now updated with our direct API approach and phased implementation plan! 🚀

