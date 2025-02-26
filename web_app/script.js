/**
 * Polly Web App
 * 
 * This script handles the WebSocket communication with the Raspberry Pi
 * and the integration with OpenAI APIs.
 */

// DOM Elements
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const piIpInput = document.getElementById('pi-ip');
const openaiKeyInput = document.getElementById('openai-key');
const connectBtn = document.getElementById('connect-btn');
const playAudioBtn = document.getElementById('play-audio-btn');
const testBtn = document.getElementById('test-btn');
const conversation = document.getElementById('conversation');
const audioStatusText = document.getElementById('audio-status-text');

// WebSocket connection
let socket = null;
let isConnected = false;

// Audio handling
let lastAudioReceived = null;
let audioContext = null;
let audioPlayer = null;

// Initialize the app
function init() {
    // Load saved settings from localStorage
    loadSettings();
    
    // Add event listeners
    connectBtn.addEventListener('click', toggleConnection);
    playAudioBtn.addEventListener('click', playLastAudio);
    testBtn.addEventListener('click', testConnection);
    
    // Initialize Web Audio API
    try {
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        audioContext = new AudioContext();
    } catch (e) {
        addMessage('system', 'Web Audio API is not supported in this browser. Audio playback will not work.');
    }
}

// Load settings from localStorage
function loadSettings() {
    const savedIp = localStorage.getItem('polly_pi_ip');
    const savedKey = localStorage.getItem('polly_openai_key');
    
    if (savedIp) {
        piIpInput.value = savedIp;
    }
    
    if (savedKey) {
        openaiKeyInput.value = savedKey;
    }
}

// Save settings to localStorage
function saveSettings() {
    localStorage.setItem('polly_pi_ip', piIpInput.value);
    localStorage.setItem('polly_openai_key', openaiKeyInput.value);
}

// Toggle WebSocket connection
function toggleConnection() {
    if (isConnected) {
        disconnectFromPi();
    } else {
        connectToPi();
    }
}

// Connect to Raspberry Pi via WebSocket
function connectToPi() {
    const ip = piIpInput.value.trim();
    
    if (!ip) {
        addMessage('system', 'Please enter the Raspberry Pi IP address.');
        return;
    }
    
    // Save settings
    saveSettings();
    
    // Update UI
    setConnectionStatus('connecting', 'Connecting...');
    connectBtn.disabled = true;
    
    // Create WebSocket connection
    try {
        socket = new WebSocket(`ws://${ip}:8765`);
        
        // Connection opened
        socket.addEventListener('open', (event) => {
            isConnected = true;
            setConnectionStatus('connected', 'Connected');
            connectBtn.textContent = 'Disconnect';
            connectBtn.disabled = false;
            addMessage('system', `Connected to Polly at ${ip}`);
        });
        
        // Listen for messages
        socket.addEventListener('message', (event) => {
            handleWebSocketMessage(event.data);
        });
        
        // Connection closed
        socket.addEventListener('close', (event) => {
            isConnected = false;
            setConnectionStatus('disconnected', 'Disconnected');
            connectBtn.textContent = 'Connect';
            connectBtn.disabled = false;
            addMessage('system', 'Disconnected from Polly');
        });
        
        // Connection error
        socket.addEventListener('error', (event) => {
            isConnected = false;
            setConnectionStatus('disconnected', 'Connection Error');
            connectBtn.textContent = 'Connect';
            connectBtn.disabled = false;
            addMessage('system', 'WebSocket connection error. Please check if the Raspberry Pi is running and accessible.');
        });
    } catch (error) {
        isConnected = false;
        setConnectionStatus('disconnected', 'Connection Error');
        connectBtn.textContent = 'Connect';
        connectBtn.disabled = false;
        addMessage('system', `Error connecting to Polly: ${error.message}`);
    }
}

// Disconnect from Raspberry Pi
function disconnectFromPi() {
    if (socket) {
        socket.close();
    }
}

// Handle WebSocket messages
async function handleWebSocketMessage(data) {
    try {
        const message = JSON.parse(data);
        
        switch (message.type) {
            case 'info':
                addMessage('system', message.data);
                break;
                
            case 'error':
                addMessage('system', `Error: ${message.data}`);
                break;
                
            case 'audio':
                // Handle audio data from Pi
                audioStatusText.textContent = 'Audio received, processing...';
                lastAudioReceived = message.data;
                playAudioBtn.disabled = false;
                
                // Process the audio with OpenAI Whisper
                const transcription = await transcribeAudio(message.data);
                addMessage('user', transcription);
                
                // Generate response with ChatGPT
                const response = await generateResponse(transcription);
                addMessage('polly', response);
                
                // Convert response to speech
                const speechAudio = await textToSpeech(response);
                
                // Send audio response back to Pi
                sendAudioResponse(speechAudio);
                
                break;
                
            case 'pong':
                addMessage('system', 'Ping test successful!');
                break;
                
            default:
                console.log('Unknown message type:', message.type);
        }
    } catch (error) {
        console.error('Error handling WebSocket message:', error);
        addMessage('system', `Error processing message: ${error.message}`);
    }
}

// Send a ping test to the Pi
function testConnection() {
    if (!isConnected || !socket) {
        addMessage('system', 'Not connected to Polly. Please connect first.');
        return;
    }
    
    socket.send(JSON.stringify({
        type: 'ping',
        data: 'Testing connection'
    }));
    
    addMessage('system', 'Sending ping test...');
}

// Play the last received audio
function playLastAudio() {
    if (!lastAudioReceived) {
        addMessage('system', 'No audio available to play.');
        return;
    }
    
    if (!audioContext) {
        addMessage('system', 'Audio playback is not supported in this browser.');
        return;
    }
    
    try {
        // Decode base64 audio data
        const base64Data = lastAudioReceived.split(',')[1];
        const binaryData = atob(base64Data);
        const arrayBuffer = new ArrayBuffer(binaryData.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        
        for (let i = 0; i < binaryData.length; i++) {
            uint8Array[i] = binaryData.charCodeAt(i);
        }
        
        // Decode audio data
        audioContext.decodeAudioData(arrayBuffer, (buffer) => {
            // Create audio source
            const source = audioContext.createBufferSource();
            source.buffer = buffer;
            source.connect(audioContext.destination);
            source.start(0);
            
            addMessage('system', 'Playing audio...');
        }, (error) => {
            addMessage('system', `Error decoding audio: ${error.message}`);
        });
    } catch (error) {
        addMessage('system', `Error playing audio: ${error.message}`);
    }
}

// Transcribe audio using OpenAI Whisper API
async function transcribeAudio(audioData) {
    const apiKey = openaiKeyInput.value.trim();
    
    if (!apiKey) {
        throw new Error('OpenAI API key is required for transcription.');
    }
    
    try {
        // For demo purposes, we'll simulate the API call
        // In a real implementation, you would send the audio to the OpenAI API
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Return a mock transcription
        return "Hello Polly, what's the weather like today?";
        
        /* Real implementation would be something like:
        
        // Convert base64 audio to blob
        const base64Data = audioData.split(',')[1];
        const binaryData = atob(base64Data);
        const arrayBuffer = new ArrayBuffer(binaryData.length);
        const uint8Array = new Uint8Array(arrayBuffer);
        
        for (let i = 0; i < binaryData.length; i++) {
            uint8Array[i] = binaryData.charCodeAt(i);
        }
        
        const blob = new Blob([uint8Array], { type: 'audio/wav' });
        
        // Create form data
        const formData = new FormData();
        formData.append('file', blob, 'audio.wav');
        formData.append('model', 'whisper-1');
        
        // Send to OpenAI API
        const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error.message);
        }
        
        return data.text;
        */
    } catch (error) {
        console.error('Transcription error:', error);
        throw new Error(`Transcription failed: ${error.message}`);
    }
}

// Generate response using ChatGPT API
async function generateResponse(text) {
    const apiKey = openaiKeyInput.value.trim();
    
    if (!apiKey) {
        throw new Error('OpenAI API key is required for generating responses.');
    }
    
    try {
        // For demo purposes, we'll simulate the API call
        // In a real implementation, you would send the text to the OpenAI API
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Return a mock response
        return "The weather today is sunny and warm. It's a perfect day to play outside!";
        
        /* Real implementation would be something like:
        
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-3.5-turbo',
                messages: [
                    {
                        role: 'system',
                        content: 'You are Polly, a friendly talking bird for children. Keep responses simple, engaging, and appropriate for young children.'
                    },
                    {
                        role: 'user',
                        content: text
                    }
                ],
                max_tokens: 150
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error.message);
        }
        
        return data.choices[0].message.content;
        */
    } catch (error) {
        console.error('Response generation error:', error);
        throw new Error(`Response generation failed: ${error.message}`);
    }
}

// Convert text to speech
async function textToSpeech(text) {
    try {
        // For demo purposes, we'll use the browser's built-in speech synthesis
        // In a real implementation, you might use a more sophisticated TTS service
        
        return new Promise((resolve, reject) => {
            // Create SpeechSynthesisUtterance
            const utterance = new SpeechSynthesisUtterance(text);
            
            // Configure voice
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            // Get available voices
            const voices = window.speechSynthesis.getVoices();
            
            // Try to find a child-like voice
            const childVoice = voices.find(voice => 
                voice.name.includes('child') || 
                voice.name.includes('female') || 
                voice.name.includes('girl')
            );
            
            if (childVoice) {
                utterance.voice = childVoice;
            }
            
            // Create an audio context and destination node
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const destination = audioContext.createMediaStreamDestination();
            
            // Create a media recorder to capture the audio
            const mediaRecorder = new MediaRecorder(destination.stream);
            const audioChunks = [];
            
            mediaRecorder.addEventListener('dataavailable', event => {
                audioChunks.push(event.data);
            });
            
            mediaRecorder.addEventListener('stop', () => {
                // Create blob from audio chunks
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                
                // Convert blob to base64
                const reader = new FileReader();
                reader.readAsDataURL(audioBlob);
                reader.onloadend = () => {
                    const base64data = reader.result;
                    resolve(base64data);
                };
            });
            
            // Start recording
            mediaRecorder.start();
            
            // Speak the text
            window.speechSynthesis.speak(utterance);
            
            // Stop recording when speech ends
            utterance.onend = () => {
                mediaRecorder.stop();
            };
            
            // Handle errors
            utterance.onerror = (event) => {
                reject(new Error(`Speech synthesis error: ${event.error}`));
            };
        });
        
        /* Real implementation might use a service like AWS Polly or Google TTS:
        
        const response = await fetch('https://texttospeech.googleapis.com/v1/text:synthesize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${googleApiKey}`
            },
            body: JSON.stringify({
                input: { text },
                voice: { languageCode: 'en-US', name: 'en-US-Wavenet-F' },
                audioConfig: { audioEncoding: 'LINEAR16' }
            })
        });
        
        const data = await response.json();
        return `data:audio/wav;base64,${data.audioContent}`;
        */
    } catch (error) {
        console.error('Text-to-speech error:', error);
        throw new Error(`Text-to-speech failed: ${error.message}`);
    }
}

// Send audio response back to Pi
function sendAudioResponse(audioData) {
    if (!isConnected || !socket) {
        addMessage('system', 'Not connected to Polly. Cannot send audio response.');
        return;
    }
    
    try {
        socket.send(JSON.stringify({
            type: 'audio_response',
            data: audioData
        }));
        
        audioStatusText.textContent = 'Response sent to Polly';
        addMessage('system', 'Audio response sent to Polly');
    } catch (error) {
        console.error('Error sending audio response:', error);
        addMessage('system', `Error sending audio response: ${error.message}`);
    }
}

// Add a message to the conversation
function addMessage(type, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const paragraph = document.createElement('p');
    paragraph.textContent = text;
    
    messageDiv.appendChild(paragraph);
    conversation.appendChild(messageDiv);
    
    // Scroll to bottom
    conversation.scrollTop = conversation.scrollHeight;
}

// Set connection status
function setConnectionStatus(status, text) {
    statusIndicator.className = `status-indicator ${status}`;
    statusText.textContent = text;
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', init);
