"""
Button handling module for Polly.

This module provides functionality to detect button presses on GPIO 17.
"""

try:
    import RPi.GPIO as GPIO
except ImportError:
    # For development on non-Raspberry Pi systems
    print("Warning: RPi.GPIO not available. Using mock implementation.")
    
    class MockGPIO:
        BCM = "BCM"
        IN = "IN"
        RISING = "RISING"
        PUD_DOWN = "PUD_DOWN"
        
        def setmode(self, mode):
            print(f"GPIO.setmode({mode})")
            
        def setup(self, pin, direction, pull_up_down=None):
            pull_up_down_str = f", pull_up_down={pull_up_down}" if pull_up_down else ""
            print(f"GPIO.setup({pin}, {direction}{pull_up_down_str})")
            
        def add_event_detect(self, pin, edge, callback=None, bouncetime=None):
            bouncetime_str = f", bouncetime={bouncetime}" if bouncetime else ""
            print(f"GPIO.add_event_detect({pin}, {edge}, callback=Function{bouncetime_str})")
            
        def cleanup(self):
            print("GPIO.cleanup()")
    
    GPIO = MockGPIO()


class Button:
    """Class to handle button press detection."""
    
    def __init__(self, pin=17, callback=None, bouncetime=200):
        """
        Initialize the button handler.
        
        Args:
            pin (int): GPIO pin number (BCM mode) connected to the button.
            callback (function): Function to call when button is pressed.
            bouncetime (int): Debounce time in milliseconds.
        """
        self.pin = pin
        self.callback = callback
        self.bouncetime = bouncetime
        self.is_setup = False
        
    def setup(self):
        """Set up the GPIO pin for button detection."""
        if self.is_setup:
            return
            
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.is_setup = True
        print(f"Button setup on GPIO {self.pin}")
        
    def start_detection(self, callback=None):
        """
        Start detecting button presses.
        
        Args:
            callback (function, optional): Function to call when button is pressed.
                If provided, overrides the callback set during initialization.
        """
        if not self.is_setup:
            self.setup()
            
        # Use the provided callback or the one from initialization
        cb = callback if callback is not None else self.callback
        
        if cb is None:
            raise ValueError("No callback function provided")
            
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=cb, bouncetime=self.bouncetime)
        print(f"Button detection started on GPIO {self.pin}")
        
    def cleanup(self):
        """Clean up GPIO resources."""
        if self.is_setup:
            GPIO.cleanup()
            self.is_setup = False
            print("Button GPIO resources cleaned up")


# Example usage
if __name__ == "__main__":
    def on_button_press(channel):
        print(f"Button pressed on channel {channel}!")
        
    try:
        button = Button(pin=17, callback=on_button_press)
        button.setup()
        button.start_detection()
        
        print("Waiting for button press. Press Ctrl+C to exit.")
        # Keep the program running
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        # Clean up GPIO resources
        if 'button' in locals():
            button.cleanup()
