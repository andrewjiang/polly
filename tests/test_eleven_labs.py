#!/usr/bin/env python3
"""
Test script to interact with Eleven Labs' Conversational AI.

This script connects to Eleven Labs' API, sends a test message, and prints the response.
"""

import os
import requests
from dotenv import load_dotenv
import elevenlabs
import signal
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
import time

# Load environment variables
load_dotenv()

# Get API key from environment
ELEVEN_LABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not ELEVEN_LABS_API_KEY:
    raise ValueError("ELEVEN_LABS_API_KEY environment variable not set")

# Load agent ID from environment
AGENT_ID = os.getenv("AGENT_ID")
if not AGENT_ID:
    raise ValueError("AGENT_ID environment variable not set")

# API endpoint for Eleven Labs' Conversational AI
api_url = "https://api.elevenlabs.io/v1/conversational-ai"

# Initialize the Eleven Labs client
client = ElevenLabs(api_key=ELEVEN_LABS_API_KEY)

# Callback for when the agent responds
def agent_response_callback(response):
    print(f"Agent: {response}")
    # Wait for a short period after the agent finishes speaking
    time.sleep(2)  # Adjust the delay as needed

# Initialize the Conversation instance with the callback
conversation = Conversation(
    client,
    AGENT_ID,
    requires_auth=bool(ELEVEN_LABS_API_KEY),
    audio_interface=DefaultAudioInterface(),
    callback_agent_response=agent_response_callback,
    callback_agent_response_correction=lambda original, corrected: print(f"Agent: {original} -> {corrected}"),
    callback_user_transcript=lambda transcript: print(f"User: {transcript}"),
)

# Start the conversation
conversation.start_session()

# Handle clean shutdown on Ctrl+C
signal.signal(signal.SIGINT, lambda sig, frame: conversation.end_session())

# Wait for the conversation to end
conversation_id = conversation.wait_for_session_end()
print(f"Conversation ID: {conversation_id}") 