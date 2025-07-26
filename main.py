import machine
import time
from machine import UART, Pin, SPI
import gc
import framebuf
import neopixel
import ezFBfont
import ezFBfont_5x7_ascii_07
import json
import os

class RGBDisplay:
    def __init__(self, spi_id=0, dc_pin=5, cs_pin=6, rst_pin=7, bl_pin=8):
        """
        Initialize RGB display via SPI
        
        Args:
            spi_id: SPI interface ID
            dc_pin: Data/Command pin
            cs_pin: Chip Select pin
            rst_pin: Reset pin
            bl_pin: Backlight pin (PWM capable, optional)
        """
        # Swap width and height for 90-degree rotation
        self.width = 160
        self.height = 128
        
        # SPI configuration
        self.spi = SPI(spi_id, baudrate=40000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))
        self.dc = Pin(dc_pin, Pin.OUT)
        self.cs = Pin(cs_pin, Pin.OUT)
        self.rst = Pin(rst_pin, Pin.OUT)
        
        # Backlight PWM
        self.bl_pwm = None
        if bl_pin is not None:
            from machine import PWM
            self.bl_pwm = PWM(Pin(bl_pin))
            self.bl_pwm.freq(1000)
            self.set_backlight(1.0)  # 100% brightness by default
        
        # Initialize display
        self.init_display()
        
        # Create framebuffer (width and height swapped)
        self.buffer = bytearray(self.width * self.height * 2)  # 16-bit color
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)
        # Initialize ezFBfont with the framebuffer and font
        self.ezfont = ezFBfont.ezFBfont(self.fb, ezFBfont_5x7_ascii_07)
        
        # Clear display
        self.clear()
        
        # Font settings
        self.font_width = 6
        self.font_height = 8
        self.chars_per_line = self.width // self.font_width
        self.lines_per_screen = self.height // self.font_height
        
        # Text buffer for scrolling
        self.text_lines = []
        self.current_line = 0
    
    def set_backlight(self, brightness):
        """
        Set backlight brightness (0.0 to 1.0)
        """
        if self.bl_pwm is not None:
            brightness = max(0.0, min(1.0, brightness))
            duty = int(brightness * 65535)
            self.bl_pwm.duty_u16(duty)
    
    def backlight_on(self):
        """Turn backlight fully on (100%)"""
        self.set_backlight(1.0)
    
    def backlight_off(self):
        """Turn backlight off (0%)"""
        self.set_backlight(0.0)
    
    def init_display(self):
        """Initialize the RGB display"""
        # Reset display
        self.rst.value(0)
        time.sleep_ms(100)
        self.rst.value(1)
        time.sleep_ms(100)
        
        # Common ST7735 initialization commands
        init_commands = [
            (0x11, None),  # Sleep out
            (0x3A, b'\x05'),  # Color mode: 16-bit/pixel
            (0x36, b'\x60'),  # Memory access control: 90-degree rotation (try 0x60)
            (0x2A, b'\x00\x00\x00\x9F'),  # Column address set (0-159)
            (0x2B, b'\x00\x00\x00\x7F'),  # Row address set (0-127)
            (0x29, None),  # Display on
        ]
        
        for cmd, data in init_commands:
            self.write_cmd(cmd)
            if data:
                self.write_data(data)
            time.sleep_ms(10)
    
    def write_cmd(self, cmd):
        """Write command to display"""
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytes([cmd]))
        self.cs.value(1)
    
    def write_data(self, data):
        """Write data to display"""
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(data)
        self.cs.value(1)
    
    def clear(self, color=0x0000):
        """Clear display with specified color"""
        self.fb.fill(color)
        self.update()
    
    def update(self):
        """Update display with framebuffer content"""
        self.write_cmd(0x2C)  # Memory write
        self.write_data(self.buffer)
    
    def draw_text(self, text, x, y, color=0xFFFF):
        # Use ezFBfont to draw text
        self.ezfont.write(text, x, y, fg=color, bg=0x0000)
        self.update()
    
    def add_text_line(self, text):
        # Add a new line of text and scroll if needed (no manual rotation)
        self.text_lines.append(text)
        
        # Remove old lines if we have too many
        while len(self.text_lines) > self.lines_per_screen:
            self.text_lines.pop(0)
        
        # Redraw all lines
        self.clear()
        for i, line in enumerate(self.text_lines):
            y_pos = i * self.ezfont._font.height()
            # Truncate line if too long
            # Use ezFBfont to measure width if needed, but for now just truncate
            max_chars = self.width // self.ezfont._font.max_width()
            if len(line) > max_chars:
                line = line[:max_chars]
            self.ezfont.write(line, 0, y_pos, fg=0xFFFF, bg=0x0000)
        self.update()

class SerialAutoConfig:
    CONFIG_FILE = "serial_config.json"
    def __init__(self, uart_id=0, tx_pin=0, rx_pin=1):
        """
        Initialize serial auto-configuration for RP2040
        
        Args:
            uart_id: UART interface ID (0 or 1)
            tx_pin: TX pin number
            rx_pin: RX pin number
        """
        self.uart_id = uart_id
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.uart = None
        
        # Set GPIO4 to fixed low state
        self.gpio4 = Pin(4, Pin.OUT)
        self.gpio4.value(0)  # Set to low
        
        # Initialize WS2812 RGB LED on GPIO16
        self.led = neopixel.NeoPixel(Pin(16), 1)
        
        # Initialize display
        self.display = RGBDisplay(bl_pin=8)
        self.display.set_backlight(0.5)
             
        # Common data bit configurations
        self.data_bits = [7, 8]
        
        # Common parity settings
        self.parity_options = [None, 0, 1]  # None, EVEN, ODD
        
        # Common stop bit configurations
        self.stop_bits = [1, 2]
        
        # Display welcome message
        self.display.add_text_line("Serial Auto-Config")
        self.display.add_text_line("RP2040")
        self.display.add_text_line("=" * 20)
        print("Serial Auto-Configuration for RP2040")
        print("=" * 40)    
    
    def is_printable_text(self, data):
        """
        Check if received data contains printable text characters
        
        Args:
            data: bytes object to check
            
        Returns:
            bool: True if data contains printable text
        """
        if not data:
            return False
        
        # Convert to string and check for printable characters
        try:
            text = data.decode()
            
            # Check if at least 85% of characters are printable
            printable_count = sum(1 for c in text if c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!-$/()=?,.;:+#*")
            print("Printable " + str(printable_count / len(text)))
            return printable_count / len(text) > 0.85
            
        except:
            return False
    
    def test_configuration(self, baud_rate, data_bits=8, parity=None, stop_bits=1):
        """
        Test a specific serial configuration
        Args:
            baud_rate: Baud rate to test
            data_bits: Number of data bits
            parity: Parity setting (None, 0, 1)
            stop_bits: Number of stop bits
        Returns:
            tuple: (success, received_data, config_info)
        Note: This function waits indefinitely until enough data is received.
        """
        try:
            # Create UART with current configuration
            self.uart = UART(
                self.uart_id,
                baudrate=baud_rate,
                bits=data_bits,
                parity=parity,
                stop=stop_bits,
                tx=Pin(self.tx_pin),
                rx=Pin(self.rx_pin),
                timeout=50  # Required by constructor, ignored in logic
            )

            self.uart.read(1000) # Flush input buffer
            received_data = b''
            while True:
                if self.uart.any():
                    chunk = self.uart.read(5)
                    if chunk:
                        received_data += chunk
                        # If we have enough data, check it
                        if len(received_data) >= 15:
                            break
                time.sleep_ms(10)
            # Check if we received valid text
            if received_data and self.is_printable_text(received_data):
                config_info = {
                    'baud_rate': baud_rate,
                    'data_bits': data_bits,
                    'parity': parity,
                    'stop_bits': stop_bits
                }
                return True, received_data, config_info
            return False, received_data, None
        except Exception as e:
            print(f"Error testing configuration: {e}")
            return False, b'', None
    
    def get_configuration_string(self, baud_rate, data_bits, parity, stop_bits):
        parity_str = 'E' if parity == 0 else 'O' if parity == 1 else 'N'
        return f"Testing {baud_rate} {data_bits}{parity_str}{stop_bits}"

    def load_config_from_file(self):
        """Load serial config from filesystem if available."""
        try:
            if self.CONFIG_FILE in os.listdir():
                with open(self.CONFIG_FILE, "r") as f:
                    config = json.load(f)
                # Validate keys
                required = ["baud_rate", "data_bits", "parity", "stop_bits"]
                if all(k in config for k in required):
                    return config
        except Exception as e:
            print(f"Error loading config: {e}")
        return None

    def save_config_to_file(self, config):
        """Save working serial config to filesystem."""
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def find_working_configuration(self):
        """
        Try stored config first, then auto-detect if needed. Store new config if found.
        Returns:
            dict: Working configuration or None if none found
        """
        # Step 0: Try stored config
        config = self.load_config_from_file()
        if config:
            self.display.add_text_line("Testing stored config...")
            config_msg = self.get_configuration_string(config["baud_rate"], config["data_bits"], config["parity"], config["stop_bits"])
            self.display.add_text_line(config_msg)
            print("Testing stored config from file...")
            print(config_msg)
            success, data, valid_config = self.test_configuration(
                config["baud_rate"], config["data_bits"], config["parity"], config["stop_bits"]
            )
            if success:
                self.display.clear()
                self.display.add_text_line("STORED CONFIG OK!")
                sample = data.decode()
                self.display.add_text_line(sample)
                self.led[0] = (0, 255, 0)  # Green
                self.led.write()
                return valid_config
            else:
                self.display.add_text_line("Stored config invalid")
                print("Stored config invalid, falling back to auto-detect...")

        # Fallback: traditional method with all baud rates
        baud_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        total_configs = len(baud_rates) * len(self.data_bits) * len(self.parity_options) * len(self.stop_bits)
        current_config = 0
        self.display.add_text_line("Testing all baud rates...")
        print(f"Testing {total_configs} different configurations...")
        for baud_rate in baud_rates:
            for data_bits in self.data_bits:
                for parity in self.parity_options:
                    for stop_bits in self.stop_bits:
                        current_config += 1
                        self.led[0] = (255, 165, 0)  # Orange
                        self.led.write()
                        time.sleep_ms(50)
                        self.led[0] = (0, 0, 0)  # Off
                        self.led.write()
                        progress_msg = f"Config {current_config}/{total_configs}"
                        self.display.add_text_line(progress_msg)
                        config_msg = self.get_configuration_string(baud_rate, data_bits, parity, stop_bits)
                        self.display.add_text_line(config_msg)
                        print(f"\r{current_config}/{total_configs} {config_msg}")
                        success, data, config = self.test_configuration(
                            baud_rate, data_bits, parity, stop_bits
                        )
                        if success:
                            self.display.clear()
                            self.display.add_text_line("SUCCESS!")
                            self.display.add_text_line(config_msg)
                            print(f"\n\n✅ WORKING CONFIGURATION FOUND!")
                            print(config_msg)
                            self.led[0] = (0, 255, 0)  # Green
                            self.led.write()
                            self.save_config_to_file(config)
                            return config
        self.display.clear()
        self.display.add_text_line("NO CONFIG FOUND")
        self.display.add_text_line("Check connections")
        self.display.add_text_line("and try again")
        print(f"\n\n❌ No working configuration found")
        self.led[0] = (255, 0, 0)  # Red
        self.led.write()
        return None
    
    def monitor_serial(self, config):
        """
        Monitor serial data with the working configuration
        
        Args:
            config: Working configuration dictionary
        """
        if not config:
            print("No valid configuration to monitor")
            return
        
        # Clear display for monitoring
        self.display.clear()
        self.display.add_text_line("MONITORING SERIAL")
        self.display.add_text_line(self.get_configuration_string(config['baud_rate'], config['data_bits'], config['parity'], config['stop_bits']))
        self.display.add_text_line("=" * 20)
        
        # Set LED to cyan for monitoring mode
        self.led[0] = (0, 255, 255)  # Cyan
        self.led.write()
                
        # Recreate UART with working configuration
        self.uart = UART(
            self.uart_id,
            baudrate=config['baud_rate'],
            bits=config['data_bits'],
            parity=config['parity'],
            stop=config['stop_bits'],
            tx=Pin(self.tx_pin),
            rx=Pin(self.rx_pin),
            timeout=50
        )
        
        try:
            while True:
                if self.uart.any():
                    data = self.uart.readline()
                    if data:
                        text = data.decode()
                        self.display.add_text_line(text)
                        # Flash LED green briefly when data received
                        self.led[0] = (0, 255, 0)  # Green
                        self.led.write()
                        time.sleep_ms(100)
                        self.led[0] = (0, 255, 255)  # Back to cyan
                        self.led.write()
                        print(f"Received: {text}\n", end='')
                
                time.sleep_ms(10)
                gc.collect()  # Prevent memory issues during long monitoring
                
        except KeyboardInterrupt:
            self.display.add_text_line("MONITORING STOPPED")
            # Turn LED off when monitoring stops
            self.led[0] = (0, 0, 0)  # Off
            self.led.write()
            print("\nMonitoring stopped by user")
        except Exception as e:
            self.display.add_text_line(f"ERROR: {str(e)}")
            # Turn LED red for error
            self.led[0] = (255, 0, 0)  # Red
            self.led.write()
            print(f"Error during monitoring: {e}")

def main():
    """Main function to run the serial auto-configuration"""
    try:
        # Create auto-config instance
        auto_config = SerialAutoConfig(uart_id=0, tx_pin=0, rx_pin=1)
        
        # Find working configuration
        working_config = auto_config.find_working_configuration()
        
        if working_config:
            # Start monitoring with the working configuration
            auto_config.monitor_serial(working_config)
        else:
            print("Could not find a working serial configuration.")
            print("Check your connections and try again.")
            
    except Exception as e:
        print(f"Error in main: {e}")
        import sys
        sys.print_exception(e)

if __name__ == "__main__":
    main() 