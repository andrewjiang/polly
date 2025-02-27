"""
OpenAI API integration for Polly.

This module provides functions to interact with OpenAI's APIs:
- Whisper API for audio transcription
- ChatGPT API for conversational responses
"""

import os
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client - simplified initialization
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    logger.warning("OPENAI_API_KEY environment variable not set")

# Import OpenAI after setting up logging
from openai import OpenAI

# Try to initialize the OpenAI client with default settings
try:
    client = OpenAI()  # Uses OPENAI_API_KEY from environment by default
except TypeError as e:
    # Handle the case where 'proxies' argument is not supported
    if 'unexpected keyword argument' in str(e) and 'proxies' in str(e):
        logger.warning("OpenAI client initialization failed with proxies argument. Using default initialization.")
        import httpx
        # Create a custom httpx client without proxies
        http_client = httpx.Client()
        client = OpenAI(http_client=http_client)
    else:
        # Re-raise if it's a different TypeError
        raise

# Constants
CONVERSATION_HISTORY_FILE = "conversation_history.json"
MAX_HISTORY_LENGTH = 10  # Maximum number of conversation turns to keep

def transcribe_audio(audio_file_path):
    """
    Transcribe audio using OpenAI's Whisper API.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        
    Returns:
        str: Transcribed text
    """
    try:
        logger.info(f"Transcribing audio file: {audio_file_path}")
        
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        transcribed_text = transcript.text
        logger.info(f"Transcription successful: {transcribed_text}")
        return transcribed_text
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return "I couldn't understand the audio. Could you please try again?"

def load_conversation_history():
    """
    Load conversation history from file.
    
    Returns:
        list: List of conversation messages
    """
    try:
        if os.path.exists(CONVERSATION_HISTORY_FILE):
            with open(CONVERSATION_HISTORY_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logger.error(f"Error loading conversation history: {str(e)}")
        return []

def save_conversation_history(history):
    """
    Save conversation history to file.
    
    Args:
        history (list): List of conversation messages
    """
    try:
        # Limit history length
        if len(history) > MAX_HISTORY_LENGTH * 2:  # *2 because each turn has user and assistant messages
            history = history[-(MAX_HISTORY_LENGTH * 2):]
        
        with open(CONVERSATION_HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except Exception as e:
        logger.error(f"Error saving conversation history: {str(e)}")

def get_chatgpt_response(user_input, system_prompt=None):
    """
    Get a response from ChatGPT based on user input and conversation history.
    
    Args:
        user_input (str): User's input text
        system_prompt (str, optional): System prompt to guide the model's behavior
        
    Returns:
        str: ChatGPT's response
    """
    try:
        logger.info(f"Getting ChatGPT response for: {user_input}")
        
        # Load conversation history
        conversation_history = load_conversation_history()
        
        # Prepare messages
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system", 
                "content": "You are Polly, a helpful and friendly voice assistant. Keep your responses concise and conversational."
            })
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_input})
        
        # Get response from ChatGPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            temperature=0.7
        )
        
        assistant_response = response.choices[0].message.content
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": assistant_response})
        save_conversation_history(conversation_history)
        
        logger.info(f"ChatGPT response: {assistant_response}")
        return assistant_response
    
    except Exception as e:
        logger.error(f"Error getting ChatGPT response: {str(e)}")
        return "I'm having trouble connecting to my brain right now. Please try again later."

if __name__ == "__main__":
    # Test the module
    test_response = get_chatgpt_response("Hello, how are you today?")
    print(f"Test response: {test_response}") 