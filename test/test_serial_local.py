"""
Test script for serial auto-configuration - Local Computer Version
This script runs on a local computer to send test data to the Pi Pico
"""

import serial
import time
import sys

def send_test_data(port, baudrate=19200):
    """
    Send test serial data for testing the auto-configuration program
    """
    try:
        # Configure serial connection
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_TWO,
            timeout=1
        )
        
        print("Test Serial Data Sender")
        print("=" * 30)
        print(f"Connected to {port} at {baudrate} baud")
        print("Sending test data every 2 seconds...")
        print("Press Ctrl+C to stop")
        
        test_messages = [
            "Hello World!",
            "This is a test message",
            "Serial communication working!",
            "RP2040 MicroPython test",
            "Auto-configuration test data",
            "Testing 123...",
            "Lorem ipsum dolor sit amet",
            "The quick brown fox jumps over the lazy dog",
            "0123456789",
            "Special chars: !@#$%^&*()_+-="
        ]
        
        message_index = 0
        
        while True:
            # Send a test message
            message = test_messages[message_index % len(test_messages)]
            ser.write(message.encode('utf-8'))
            print(f"Sent: {message}")
            
            # Increment message index
            message_index += 1
            
            # Wait 2 seconds before next message
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()


def main():
    """
    Main function - choose test mode
    """
    print("Serial Test Data Sender - Local Computer Version")
    print("=" * 50)
    
    # Check if pyserial is available
    try:
        import serial
    except ImportError:
        print("Error: pyserial is not installed.")
        print("Please install it with: pip install pyserial")
        return
    
    
    # Use hardcoded port
    port = "/dev/cu.usbserial-3120"
    print(f"Using hardcoded port: {port}")
    
    send_test_data(port)

if __name__ == "__main__":
    main() 