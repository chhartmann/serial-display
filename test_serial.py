"""
Test script for serial auto-configuration
This script can be run on a second RP2040 to send test data
"""

import machine
import time
from machine import UART, Pin

def send_test_data():
    """
    Send test serial data for testing the auto-configuration program
    """
    # Configure UART for sending test data
    uart = UART(
        0,  # UART ID
        baudrate=115200,  # Standard baud rate
        bits=8,
        parity=None,
        stop=1,
        tx=Pin(0),  # TX pin
        rx=Pin(1),  # RX pin
        timeout=1000
    )
    
    print("Test Serial Data Sender")
    print("=" * 30)
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
    
    try:
        while True:
            # Send a test message
            message = test_messages[message_index % len(test_messages)]
            uart.write(message.encode('utf-8'))
            print(f"Sent: {message}")
            
            # Increment message index
            message_index += 1
            
            # Wait 2 seconds before next message
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error: {e}")

def send_continuous_data():
    """
    Send continuous data stream for testing
    """
    uart = UART(
        0,
        baudrate=115200,
        bits=8,
        parity=None,
        stop=1,
        tx=Pin(0),
        rx=Pin(1),
        timeout=1000
    )
    
    print("Continuous Data Stream")
    print("=" * 25)
    print("Sending continuous data...")
    
    counter = 0
    
    try:
        while True:
            # Send counter with timestamp
            timestamp = time.ticks_ms()
            message = f"Counter: {counter}, Time: {timestamp}\n"
            uart.write(message.encode('utf-8'))
            
            counter += 1
            time.sleep(0.5)  # Send every 500ms
            
    except KeyboardInterrupt:
        print("\nContinuous data stopped")
    except Exception as e:
        print(f"Error: {e}")

def send_binary_data():
    """
    Send binary data to test non-text detection
    """
    uart = UART(
        0,
        baudrate=115200,
        bits=8,
        parity=None,
        stop=1,
        tx=Pin(0),
        rx=Pin(1),
        timeout=1000
    )
    
    print("Binary Data Sender")
    print("=" * 20)
    print("Sending binary data...")
    
    # Create some binary data
    binary_data = bytes([0x00, 0xFF, 0x55, 0xAA, 0x01, 0x02, 0x03, 0x04, 0x05])
    
    try:
        while True:
            uart.write(binary_data)
            print(f"Sent binary data: {binary_data.hex()}")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nBinary data stopped")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """
    Main function - choose test mode
    """
    print("Serial Test Data Sender")
    print("=" * 30)
    print("Choose test mode:")
    print("1. Send test messages")
    print("2. Send continuous data")
    print("3. Send binary data")
    print("4. Exit")
    
    while True:
        try:
            choice = input("Enter choice (1-4): ").strip()
            
            if choice == "1":
                send_test_data()
                break
            elif choice == "2":
                send_continuous_data()
                break
            elif choice == "3":
                send_binary_data()
                break
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main() 