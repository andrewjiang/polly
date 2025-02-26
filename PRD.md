# **Product Requirements Document (PRD) – Polly the ChatGPT-Powered Talking Bird**

## **1. Product Overview**
Polly is a stuffed bird with an embedded Raspberry Pi 4 that enables natural voice interaction for children. It listens, responds intelligently using ChatGPT, and provides an engaging, interactive experience. Polly is activated via a hidden push button in its wing and records speech until 2 seconds of silence. It then sends the recorded speech to a connected smartphone via Wi-Fi, where the phone processes the audio, generates a ChatGPT-powered response, and sends back Polly's reply using text-to-speech.

## **2. Key Features & Functional Requirements**
### **Core Features (MVP)**
✅ **Embedded Electronics:** Electronics are housed in a removable module for easy maintenance.  
✅ **Voice Activation:** Push button inside the wing activates Polly. Future versions may add a wake word.  
✅ **Speech Processing:**
   - Polly records audio until 2 seconds of silence.
   - Background noise filtering ensures clear speech capture.
✅ **ChatGPT Integration:**  
   - Polly connects to a smartphone via Wi-Fi hotspot and sends recorded audio.  
   - The phone's web app transcribes the audio using OpenAI Whisper.  
   - The transcribed text is sent to ChatGPT to generate a response.  
   - The response is converted to speech using AWS Polly / Google TTS.  
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

## **3. Hardware Requirements (Updated for Your Order)**
| Component         | Model / Details |
|------------------|----------------|
| **Main Board**   | Raspberry Pi 4 Model B (4GB) - CanaKit Starter PRO Kit |
| **Microphone**   | **3.5mm Lavalier Mic (via Plugable USB Audio Adapter)** |
| **Speaker**      | **HONKYOB USB Mini Speaker** (USB-powered) |
| **Push Button**  | **Lilypad Momentary Push Button** (Hidden inside the wing, connected to GPIO 17) |
| **Power Supply** | 5V 3A (from CanaKit) / USB Power Bank for portability |
| **Connectivity** | Wi-Fi (connecting to phone hotspot) |

## **4. Software Requirements (Updated for USB Audio Adapter)**
| Component | Tool / Library |
|-----------|---------------|
| **Voice Activation (Button)** | Python script detecting GPIO 17 button press |
| **Audio Capture & Processing** | `PyAudio` + Noise filtering (`webrtcvad`) via **USB sound card** |
| **Wi-Fi Communication** | Web app interface to receive/send audio |
| **Speech-to-Text (STT)** | OpenAI Whisper API (on phone web app) |
| **AI Response** | OpenAI ChatGPT API (on phone web app) |
| **Text-to-Speech (TTS)** | Polly's voice via AWS Polly or Google TTS (on phone web app) |
| **Audio Playback** | Routed through **USB sound adapter** (not HDMI) |

## **5. User Flow (Updated for Web App)**
1. **User presses the button (hidden in Polly's wing, connected to GPIO 17).**  
2. **Polly starts listening and records the child's speech.**  
   - Polly stops recording when it detects 2 seconds of silence.  
   - **Audio is captured via the 3.5mm microphone connected to the USB sound card.**
   - Background noise is filtered for clarity.  
   - Polly plays a simple immediate response for responsiveness.
3. **Polly sends the recording to a connected phone via Wi-Fi hotspot.**  
   - The phone web app transcribes the audio using OpenAI Whisper.  
   - The transcribed text is sent to ChatGPT to generate a response.  
   - The response is converted to speech using AWS Polly / Google TTS.  
4. **The phone sends the synthesized audio back to Polly.**  
5. **Polly plays the response using its USB-powered speaker.**  
6. **Polly goes into sleep mode until the button is pressed again.**  

---

## **🔄 Next Steps (Updated)**
1. **Set up Raspberry Pi OS** on the included microSD card.  
2. **Configure USB sound adapter** to recognize both the **3.5mm microphone and USB speaker.**  
3. **Test push button integration on GPIO 17.**  
4. **Write & test Python scripts** for:
   - Button press detection
   - Audio capture from **3.5mm mic via USB sound card**
   - Audio playback through **USB speaker**
   - Sending/receiving messages via web app interface
5. **Develop a simple web app** for iPhone to process audio and generate responses.
6. **Assemble Polly**: Secure the microphone, speaker, and button inside the stuffed toy.  
7. **Test full interaction loop** (press button → record → process via web app → speak response).  

---

Your PRD is now fully updated based on your order! 🚀 Let me know when you're ready to set up the Raspberry Pi OS. 👌

