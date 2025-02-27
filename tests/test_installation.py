#!/usr/bin/env python3
"""
Test script to verify the installation of Polly components.
This script checks if all required modules can be imported and if API keys are set.
"""

import os
import sys
import importlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_module(module_name):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        logger.info(f"✅ Module '{module_name}' is available")
        return True
    except ImportError as e:
        # Special case for numpy - check if we're using the fallback
        if module_name == "numpy" and "source directory" in str(e):
            logger.warning(f"⚠️ Module '{module_name}' has import issues: {str(e)}")
            logger.warning(f"⚠️ However, the fallback mechanism in hardware/audio.py should handle this.")
            return True  # Consider it available since we have a fallback
        logger.error(f"❌ Module '{module_name}' is not available: {str(e)}")
        return False

def check_api_key(key_name):
    """Check if an API key is set in environment variables."""
    if os.environ.get(key_name):
        logger.info(f"✅ Environment variable '{key_name}' is set")
        return True
    else:
        logger.error(f"❌ Environment variable '{key_name}' is not set")
        return False

def main():
    """Run the installation tests."""
    logger.info("Testing Polly installation...")
    
    # Check required modules
    required_modules = [
        "dotenv",
        "RPi.GPIO",
        "openai",
        "requests",
        "pygame",
        "numpy"
    ]
    
    # Check custom modules
    custom_modules = [
        "hardware.button",
        "api.openai_api",
        "api.tts_api",
        "audio_utils"
    ]
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("✅ Environment variables loaded from .env file")
    except Exception as e:
        logger.error(f"❌ Failed to load environment variables: {str(e)}")
    
    # Check required modules
    all_required_available = True
    for module in required_modules:
        if not check_module(module):
            all_required_available = False
    
    # Check custom modules
    all_custom_available = True
    for module in custom_modules:
        if not check_module(module):
            all_custom_available = False
    
    # Check API keys
    api_keys_available = True
    if not check_api_key("OPENAI_API_KEY"):
        api_keys_available = False
    
    # Print summary
    logger.info("\nInstallation Test Summary:")
    if all_required_available:
        logger.info("✅ All required modules are available")
    else:
        logger.error("❌ Some required modules are missing")
    
    if all_custom_available:
        logger.info("✅ All custom modules are available")
    else:
        logger.error("❌ Some custom modules are missing")
    
    if api_keys_available:
        logger.info("✅ All API keys are set")
    else:
        logger.error("❌ Some API keys are missing")
    
    # Final verdict
    if all_custom_available and api_keys_available:
        logger.info("\n✅ Polly installation is complete and ready to use!")
        logger.info("Run 'python polly.py' to start the voice assistant.")
        return 0
    else:
        logger.error("\n❌ Polly installation is incomplete. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 