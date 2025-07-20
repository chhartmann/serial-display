import machine
import time
from machine import UART, Pin, SPI
import gc
import framebuf

class BaudRateDetector:
    def __init__(self, rx_pin=1):
        """
        Initialize baud rate detector
        
        Args:
            rx_pin: RX pin number for pulse measurement
        """
        self.rx_pin = Pin(rx_pin, Pin.IN)
        self.pulse_widths = []
        self.min_samples = 10
        self.max_samples = 50
        self.timeout_ms = 5000  # 5 second timeout
        
    def measure_pulse_widths(self):
        """
        Measure pulse widths in the incoming signal
        
        Returns:
            list: List of pulse widths in microseconds
        """
        pulse_widths = []
        start_time = time.ticks_ms()
        
        # Wait for first edge
        initial_state = self.rx_pin.value()
        
        while time.ticks_diff(time.ticks_ms(), start_time) < self.timeout_ms:
            # Wait for edge change
            while self.rx_pin.value() == initial_state:
                if time.ticks_diff(time.ticks_ms(), start_time) > self.timeout_ms:
                    break
                time.sleep_us(10)
            
            if time.ticks_diff(time.ticks_ms(), start_time) > self.timeout_ms:
                break
            
            # Measure pulse width
            pulse_start = time.ticks_us()
            current_state = self.rx_pin.value()
            
            # Wait for next edge
            while self.rx_pin.value() == current_state:
                if time.ticks_diff(time.ticks_ms(), start_time) > self.timeout_ms:
                    break
                time.sleep_us(10)
            
            if time.ticks_diff(time.ticks_ms(), start_time) > self.timeout_ms:
                break
            
            pulse_end = time.ticks_us()
            pulse_width = time.ticks_diff(pulse_end, pulse_start)
            
            if pulse_width > 0 and pulse_width < 1000000:  # Reasonable range (1ms to 1s)
                pulse_widths.append(pulse_width)
            
            # Limit number of samples
            if len(pulse_widths) >= self.max_samples:
                break
        
        return pulse_widths
    
    def detect_baud_rate(self):
        """
        Detect baud rate from pulse width measurements
        
        Returns:
            int: Detected baud rate or None if detection failed
        """
        print("Measuring pulse widths...")
        pulse_widths = self.measure_pulse_widths()
        
        if len(pulse_widths) < self.min_samples:
            print(f"Not enough samples: {len(pulse_widths)} < {self.min_samples}")
            return None
        
        # Find the smallest pulse width (shortest bit time)
        min_pulse = min(pulse_widths)
        print(f"Smallest pulse width: {min_pulse} us")
        
        # Calculate baud rate from bit time
        # Bit time = 1 / baud_rate
        # For UART: 1 bit = 1 / baud_rate seconds
        bit_time_us = min_pulse
        baud_rate = int(1000000 / bit_time_us)  # Convert to baud rate
        
        print(f"Calculated baud rate: {baud_rate}")
        
        # Round to nearest standard baud rate
        standard_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        closest_rate = min(standard_rates, key=lambda x: abs(x - baud_rate))
        
        # Check if the detected rate is reasonable
        tolerance = 0.1  # 10% tolerance
        if abs(closest_rate - baud_rate) / baud_rate <= tolerance:
            print(f"Detected baud rate: {closest_rate}")
            return closest_rate
        else:
            print(f"Detected rate {baud_rate} too far from standard {closest_rate}")
            return None
    
    def analyze_signal_characteristics(self):
        """
        Analyze signal characteristics for better detection
        
        Returns:
            dict: Signal analysis results
        """
        pulse_widths = self.measure_pulse_widths()
        
        if len(pulse_widths) < 5:
            return None
        
        # Calculate statistics
        min_pulse = min(pulse_widths)
        max_pulse = max(pulse_widths)
        avg_pulse = sum(pulse_widths) / len(pulse_widths)
        
        # Check for consistent timing (low variance indicates good signal)
        variance = sum((p - avg_pulse) ** 2 for p in pulse_widths) / len(pulse_widths)
        std_dev = variance ** 0.5
        
        return {
            'min_pulse': min_pulse,
            'max_pulse': max_pulse,
            'avg_pulse': avg_pulse,
            'std_dev': std_dev,
            'samples': len(pulse_widths),
            'consistency': avg_pulse / std_dev if std_dev > 0 else 0
        }

class RGBDisplay:
    def __init__(self, spi_id=0, dc_pin=8, cs_pin=9, rst_pin=12):
        """
        Initialize RGB display via SPI
        
        Args:
            spi_id: SPI interface ID
            dc_pin: Data/Command pin
            cs_pin: Chip Select pin
            rst_pin: Reset pin
        """
        self.width = 128
        self.height = 160
        
        # SPI configuration
        self.spi = SPI(spi_id, baudrate=40000000, polarity=0, phase=0)
        self.dc = Pin(dc_pin, Pin.OUT)
        self.cs = Pin(cs_pin, Pin.OUT)
        self.rst = Pin(rst_pin, Pin.OUT)
        
        # Initialize display
        self.init_display()
        
        # Create framebuffer
        self.buffer = bytearray(self.width * self.height * 2)  # 16-bit color
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)
        
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
            (0x36, b'\xC8'),  # Memory access control
            (0x2A, b'\x00\x00\x00\x7F'),  # Column address set
            (0x2B, b'\x00\x00\x00\x9F'),  # Row address set
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
        """Draw text at specified position"""
        self.fb.text(text, x, y, color)
    
    def add_text_line(self, text):
        """Add a new line of text and scroll if needed"""
        # Add new line
        self.text_lines.append(text)
        
        # Remove old lines if we have too many
        while len(self.text_lines) > self.lines_per_screen:
            self.text_lines.pop(0)
        
        # Redraw all lines
        self.clear()
        for i, line in enumerate(self.text_lines):
            y_pos = i * self.font_height
            # Truncate line if too long
            if len(line) > self.chars_per_line:
                line = line[:self.chars_per_line]
            self.draw_text(line, 0, y_pos)
        
        self.update()

class SerialAutoConfig:
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
        self.led = Pin(25, Pin.OUT)  # Built-in LED for status indication
        
        # Initialize display
        self.display = RGBDisplay()
        
        # Initialize baud rate detector
        self.baud_detector = BaudRateDetector(rx_pin)
        
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
    
    def detect_baud_rate(self):
        """
        Detect baud rate using pulse width measurement
        
        Returns:
            int: Detected baud rate or None if detection failed
        """
        self.display.add_text_line("Detecting baud rate...")
        self.display.add_text_line("Please send data")
        
        # Blink LED to indicate detection in progress
        for _ in range(3):
            self.led.on()
            time.sleep_ms(200)
            self.led.off()
            time.sleep_ms(200)
        
        # Start detection
        detected_baud = self.baud_detector.detect_baud_rate()
        
        if detected_baud:
            self.display.add_text_line(f"Detected: {detected_baud}")
            print(f"Baud rate detected: {detected_baud}")
            return detected_baud
        else:
            self.display.add_text_line("Detection failed")
            print("Baud rate detection failed")
            return None
    
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
            text = data.decode('utf-8', errors='ignore')
            if not text.strip():
                return False
            
            # Check if at least 50% of characters are printable
            printable_count = sum(1 for c in text if c.isprintable() or c.isspace())
            return printable_count / len(text) > 0.5
            
        except UnicodeDecodeError:
            return False
    
    def test_configuration(self, baud_rate, data_bits=8, parity=None, stop_bits=1, timeout=1000):
        """
        Test a specific serial configuration
        
        Args:
            baud_rate: Baud rate to test
            data_bits: Number of data bits
            parity: Parity setting (None, 0, 1)
            stop_bits: Number of stop bits
            timeout: Timeout in milliseconds
            
        Returns:
            tuple: (success, received_data, config_info)
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
                timeout=timeout
            )
            
            # Clear any existing data
            self.uart.read()
            
            # Wait for data with timeout
            start_time = time.ticks_ms()
            received_data = b''
            
            while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
                if self.uart.any():
                    chunk = self.uart.read()
                    if chunk:
                        received_data += chunk
                        # If we have enough data, check it
                        if len(received_data) >= 10:
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
    
    def find_working_configuration(self):
        """
        Find working configuration using detected baud rate
        
        Returns:
            dict: Working configuration or None if none found
        """
        # First, try to detect baud rate
        detected_baud = self.detect_baud_rate()
        
        if detected_baud:
            # Use detected baud rate and test other parameters
            self.display.add_text_line("Testing with detected")
            self.display.add_text_line(f"baud rate: {detected_baud}")
            
            total_configs = len(self.data_bits) * len(self.parity_options) * len(self.stop_bits)
            current_config = 0
            
            for data_bits in self.data_bits:
                for parity in self.parity_options:
                    for stop_bits in self.stop_bits:
                        current_config += 1
                        
                        # Blink LED to show progress
                        self.led.toggle()
                        
                        # Update display with progress
                        progress_msg = f"Config {current_config}/{total_configs}"
                        self.display.add_text_line(progress_msg)
                        
                        config_msg = f"{data_bits} bits, {detected_baud} baud"
                        self.display.add_text_line(config_msg)
                        
                        parity_str = 'EVEN' if parity == 0 else 'ODD' if parity == 1 else 'NONE'
                        stop_msg = f"Parity: {parity_str}, Stop: {stop_bits}"
                        self.display.add_text_line(stop_msg)
                        
                        print(f"\rTesting config {current_config}/{total_configs}: "
                              f"{detected_baud} baud, {data_bits} data bits, "
                              f"parity={'EVEN' if parity == 0 else 'ODD' if parity == 1 else 'NONE'}, "
                              f"{stop_bits} stop bits", end='')
                        
                        success, data, config = self.test_configuration(
                            detected_baud, data_bits, parity, stop_bits
                        )
                        
                        if success:
                            # Clear display and show success
                            self.display.clear()
                            self.display.add_text_line("SUCCESS!")
                            self.display.add_text_line(f"Baud: {config['baud_rate']}")
                            self.display.add_text_line(f"Data: {config['data_bits']} bits")
                            self.display.add_text_line(f"Parity: {parity_str}")
                            self.display.add_text_line(f"Stop: {config['stop_bits']}")
                            self.display.add_text_line("Sample data:")
                            
                            # Show sample data
                            sample = data[:50].decode('utf-8', errors='replace')
                            self.display.add_text_line(sample)
                            
                            print(f"\n\n✅ WORKING CONFIGURATION FOUND!")
                            print(f"Baud Rate: {config['baud_rate']}")
                            print(f"Data Bits: {config['data_bits']}")
                            print(f"Parity: {'EVEN' if config['parity'] == 0 else 'ODD' if config['parity'] == 1 else 'NONE'}")
                            print(f"Stop Bits: {config['stop_bits']}")
                            print(f"Sample received data: {data[:100]}")
                            
                            # Keep LED on to indicate success
                            self.led.on()
                            return config
            
            # If detection failed, fall back to traditional method
            self.display.add_text_line("Detection failed")
            self.display.add_text_line("Falling back to")
            self.display.add_text_line("traditional method")
            
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
                        
                        # Blink LED to show progress
                        self.led.toggle()
                        
                        # Update display with progress
                        progress_msg = f"Config {current_config}/{total_configs}"
                        self.display.add_text_line(progress_msg)
                        
                        config_msg = f"{baud_rate} baud, {data_bits} bits"
                        self.display.add_text_line(config_msg)
                        
                        parity_str = 'EVEN' if parity == 0 else 'ODD' if parity == 1 else 'NONE'
                        stop_msg = f"Parity: {parity_str}, Stop: {stop_bits}"
                        self.display.add_text_line(stop_msg)

                        print(f"\rTesting config {current_config}/{total_configs}: "
                              f"{baud_rate} baud, {data_bits} data bits, "
                              f"parity={'EVEN' if parity == 0 else 'ODD' if parity == 1 else 'NONE'}, "
                              f"{stop_bits} stop bits", end='')
                        
                        success, data, config = self.test_configuration(
                            baud_rate, data_bits, parity, stop_bits
                        )
                        
                        if success:
                            # Clear display and show success
                            self.display.clear()
                            self.display.add_text_line("SUCCESS!")
                            self.display.add_text_line(f"Baud: {config['baud_rate']}")
                            self.display.add_text_line(f"Data: {config['data_bits']} bits")
                            self.display.add_text_line(f"Parity: {parity_str}")
                            self.display.add_text_line(f"Stop: {config['stop_bits']}")
                            self.display.add_text_line("Sample data:")
                            
                            # Show sample data
                            sample = data[:50].decode('utf-8', errors='replace')
                            self.display.add_text_line(sample)
                            
                            print(f"\n\n✅ WORKING CONFIGURATION FOUND!")
                            print(f"Baud Rate: {config['baud_rate']}")
                            print(f"Data Bits: {config['data_bits']}")
                            print(f"Parity: {'EVEN' if config['parity'] == 0 else 'ODD' if config['parity'] == 1 else 'NONE'}")
                            print(f"Stop Bits: {config['stop_bits']}")
                            print(f"Sample received data: {data[:100]}")
                            
                            # Keep LED on to indicate success
                            self.led.on()
                            return config
        
        # No configuration found
        self.display.clear()
        self.display.add_text_line("NO CONFIG FOUND")
        self.display.add_text_line("Check connections")
        self.display.add_text_line("and try again")
        
        print(f"\n\n❌ No working configuration found")
        self.led.off()
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
        self.display.add_text_line(f"Baud: {config['baud_rate']}")
        self.display.add_text_line(f"Data: {config['data_bits']} bits")
        parity_str = 'EVEN' if config['parity'] == 0 else 'ODD' if config['parity'] == 1 else 'NONE'
        self.display.add_text_line(f"Parity: {parity_str}")
        self.display.add_text_line(f"Stop: {config['stop_bits']}")
        self.display.add_text_line("=" * 20)
        
        print(f"\n📡 Monitoring serial data with configuration:")
        print(f"Baud Rate: {config['baud_rate']}")
        print(f"Data Bits: {config['data_bits']}")
        print(f"Parity: {'EVEN' if config['parity'] == 0 else 'ODD' if config['parity'] == 1 else 'NONE'}")
        print(f"Stop Bits: {config['stop_bits']}")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 50)
        
        # Recreate UART with working configuration
        self.uart = UART(
            self.uart_id,
            baudrate=config['baud_rate'],
            bits=config['data_bits'],
            parity=config['parity'],
            stop=config['stop_bits'],
            tx=Pin(self.tx_pin),
            rx=Pin(self.rx_pin),
            timeout=1000
        )
        
        try:
            while True:
                if self.uart.any():
                    data = self.uart.read()
                    if data:
                        try:
                            text = data.decode('utf-8', errors='replace')
                            # Clean up text for display
                            text = text.replace('\r', '').replace('\n', ' ')
                            if text.strip():
                                self.display.add_text_line(f"RX: {text}")
                            print(f"Received: {text}", end='')
                        except:
                            hex_data = data.hex()
                            self.display.add_text_line(f"HEX: {hex_data}")
                            print(f"Received (hex): {hex_data}")
                
                time.sleep_ms(10)
                gc.collect()  # Prevent memory issues during long monitoring
                
        except KeyboardInterrupt:
            self.display.add_text_line("MONITORING STOPPED")
            print("\nMonitoring stopped by user")
        except Exception as e:
            self.display.add_text_line(f"ERROR: {str(e)}")
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