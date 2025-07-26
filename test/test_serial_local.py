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
            stopbits=serial.STOPBITS_ONE,
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

def send_continuous_data(port, baudrate=115200):
    """
    Send continuous data stream for testing
    """
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        
        print("Continuous Data Stream")
        print("=" * 25)
        print(f"Connected to {port} at {baudrate} baud")
        print("Sending continuous data...")
        
        counter = 0
        
        while True:
            # Send counter with timestamp
            timestamp = int(time.time() * 1000)
            message = f"Counter: {counter}, Time: {timestamp}\n"
            ser.write(message.encode('utf-8'))
            
            counter += 1
            time.sleep(0.5)  # Send every 500ms
            
    except KeyboardInterrupt:
        print("\nContinuous data stopped")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

def send_binary_data(port, baudrate=115200):
    """
    Send binary data to test non-text detection
    """
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        
        print("Binary Data Sender")
        print("=" * 20)
        print(f"Connected to {port} at {baudrate} baud")
        print("Sending binary data...")
        
        # Create some binary data
        binary_data = bytes([0x00, 0xFF, 0x55, 0xAA, 0x01, 0x02, 0x03, 0x04, 0x05])
        
        while True:
            ser.write(binary_data)
            print(f"Sent binary data: {binary_data.hex()}")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nBinary data stopped")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

def list_available_ports():
    """
    List available serial ports
    """
    import serial.tools.list_ports
    
    print("Available serial ports:")
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found")
    else:
        for port in ports:
            print(f"  {port.device}: {port.description}")

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
    
    # List available ports
    list_available_ports()
    print()
    
    # Use hardcoded port
    port = "/dev/cu.usbserial-3120"
    print(f"Using hardcoded port: {port}")
    
    # Get baudrate
    baudrate_input = input("Enter baudrate (default 115200): ").strip()
    baudrate = int(baudrate_input) if baudrate_input else 115200
    
    print()
    print("Choose test mode:")
    print("1. Send test messages")
    print("2. Send continuous data")
    print("3. Send binary data")
    print("4. Exit")
    
    while True:
        try:
            choice = input("Enter choice (1-4): ").strip()
            
            if choice == "1":
                send_test_data(port, baudrate)
                break
            elif choice == "2":
                send_continuous_data(port, baudrate)
                break
            elif choice == "3":
                send_binary_data(port, baudrate)
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