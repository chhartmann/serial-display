# Serial Auto-Configuration for RP2040 with RGB Display

This MicroPython program automatically configures the serial interface on a Raspberry Pi Pico (RP2040) to receive valid text characters. It uses **intelligent baud rate detection** by measuring pulse widths in the incoming signal, combined with traditional configuration testing. All output is displayed on a connected 128x160 RGB display via SPI.

## Features

- **Intelligent Baud Rate Detection**: Measures pulse widths to automatically determine the correct baud rate
- **Automatic Configuration**: Tests multiple data bits, parity settings, and stop bits with the detected baud rate
- **Fallback Method**: Falls back to traditional testing if detection fails
- **Text Detection**: Validates received data to ensure it contains printable text characters
- **Visual Feedback**: Uses the built-in LED to indicate progress and success
- **RGB Display Output**: Shows all status and received data on a 128x160 SPI RGB display
- **Real-time Monitoring**: Once a working configuration is found, continuously monitors incoming serial data
- **Memory Management**: Includes garbage collection to prevent memory issues during long monitoring sessions

## How Baud Rate Detection Works

### 1. Pulse Width Measurement
The program measures the width of pulses in the incoming serial signal:
- Monitors the RX pin for edge transitions
- Records the time between transitions
- Collects multiple samples for accuracy

### 2. Baud Rate Calculation
- Finds the smallest pulse width (shortest bit time)
- Calculates baud rate: `baud_rate = 1,000,000 / bit_time_us`
- Matches to nearest standard baud rate with 10% tolerance

### 3. Configuration Testing
Once the baud rate is detected:
- Tests different data bits (7, 8)
- Tests different parity settings (None, Even, Odd)
- Tests different stop bits (1, 2)
- Only 12 configurations instead of 96!

## Hardware Requirements

- Raspberry Pi Pico (RP2040) or compatible board
- Serial device connected to UART pins (default: TX=GP0, RX=GP1)
- 128x160 RGB display connected via SPI (e.g., ST7735)

## Pin Configuration

### UART Pins
- **TX Pin**: GPIO 0 (Pin 1)
- **RX Pin**: GPIO 1 (Pin 2)

### Display Pins (SPI)
- **SPI SCK**: GPIO 2 (Pin 4) - Fixed by SPI interface
- **SPI MOSI**: GPIO 3 (Pin 5) - Fixed by SPI interface
- **DC Pin**: GPIO 5 (Pin 7) - Data/Command control
- **CS Pin**: GPIO 6 (Pin 9) - Chip Select
- **RST Pin**: GPIO 7 (Pin 10) - Reset

### Backlight Pin (PWM)
- **BL Pin**: GPIO 8 (Pin 11) - Backlight control (PWM, default 50% brightness)

### Status LED
- **LED**: GPIO 25 (Built-in LED)

You can modify these in the `SerialAutoConfig` constructor and `RGBDisplay` constructor if needed.

## Installation

1. Copy `main.py` to your RP2040 board
2. Connect the RGB display to the SPI pins
3. Connect your serial device to the UART pins
4. Reset the board to run the program automatically

## How It Works

### 1. Display Initialization
The program starts by initializing the RGB display and showing a welcome message.

### 2. Baud Rate Detection
- Displays "Detecting baud rate..." and "Please send data"
- LED blinks 3 times to indicate detection is starting
- Measures pulse widths in the incoming signal
- Calculates and displays the detected baud rate

### 3. Configuration Testing
With the detected baud rate, the program tests:
- **Data Bits**: 7, 8
- **Parity**: None, Even, Odd
- **Stop Bits**: 1, 2

Total: Only 12 configurations instead of 96!

### 4. Fallback Method
If baud rate detection fails:
- Falls back to traditional method
- Tests all standard baud rates (9600 to 921600)
- Tests all combinations (96 configurations)

### 5. Visual Progress
- LED blinks during testing to show progress
- Display shows current configuration being tested
- Real-time status updates on the display

### 6. Success Detection
- LED stays on when a working configuration is found
- Display shows the working configuration details
- Sample received data is displayed

### 7. Continuous Monitoring
Once a working configuration is found, the program:
- Recreates the UART with the working settings
- Continuously monitors incoming serial data
- Displays received text on the RGB display in real-time

## Display Features

### Text Scrolling
- Automatically scrolls text when screen is full
- Maintains history of recent messages
- Clean, readable font optimized for 128x160 resolution

### Status Information
- Shows baud rate detection progress
- Displays current configuration being tested
- Shows working configuration when found
- Shows real-time received data

### Error Handling
- Displays error messages on screen
- Shows connection status
- Indicates when monitoring stops

## Usage

### Basic Usage
```python
# The program runs automatically when the board starts
# Just upload main.py and reset the board
```

### Custom Configuration
```python
# Modify the SerialAutoConfig constructor for different pins
auto_config = SerialAutoConfig(uart_id=1, tx_pin=4, rx_pin=5)

# Modify display pins
# Add backlight pin (BL) with PWM, e.g. GPIO8
display = RGBDisplay(spi_id=1, dc_pin=10, cs_pin=11, rst_pin=13, bl_pin=8)
display.set_backlight(0.5)  # Set to 50% brightness
```

### Manual Testing
```python
# Test a specific configuration
success, data, config = auto_config.test_configuration(
    baud_rate=115200,
    data_bits=8,
    parity=None,
    stop_bits=1
)
```

## Display Output Examples

### During Baud Rate Detection
```
Serial Auto-Config
RP2040
====================
Detecting baud rate...
Please send data
Detected: 115200
```

### During Configuration Testing
```
Testing with detected
baud rate: 115200
Config 1/12
8 bits, 115200 baud
Parity: NONE, Stop: 1
```

### When Configuration Found
```
SUCCESS!
Baud: 115200
Data: 8 bits
Parity: NONE
Stop: 1
Sample data:
Hello World!
```

### During Monitoring
```
MONITORING SERIAL
Baud: 115200
Data: 8 bits
Parity: NONE
Stop: 1
====================
RX: Hello World!
RX: Another message
RX: Test data 123
```

## Troubleshooting

### Baud Rate Detection Fails
1. Ensure your device is sending continuous data
2. Check signal quality and connections
3. Try sending repetitive patterns (like "AAAAA")
4. The program will automatically fall back to traditional method

### Display Not Working
1. Check SPI connections (SCK, MOSI, DC, CS, RST)
2. Verify display power supply
3. Check if display is compatible with ST7735 driver
4. Try different SPI pins if needed

### No Working Configuration Found
1. Check your serial device connections
2. Ensure the device is sending data
3. Try connecting TX to RX for a loopback test
4. Verify your device's serial settings

### Memory Issues
- The program includes garbage collection
- If you experience memory issues, reduce the timeout or number of configurations tested

### LED Not Blinking
- Check if the LED pin is correct for your board
- Some boards may use different LED pins

## Customization

### Modify Detection Settings
```python
# In the BaudRateDetector.__init__ method:
self.min_samples = 5      # Fewer samples for faster detection
self.max_samples = 30     # Fewer samples to collect
self.timeout_ms = 3000    # Shorter timeout
```

### Modify Display Settings
```python
# In the RGBDisplay.__init__ method:
self.spi = SPI(1, baudrate=40000000, polarity=0, phase=0)  # Different SPI
self.dc = Pin(10, Pin.OUT)  # Different DC pin
self.cs = Pin(11, Pin.OUT)  # Different CS pin
self.rst = Pin(13, Pin.OUT)  # Different RST pin
```

### Modify Tested Configurations
```python
# In the SerialAutoConfig.__init__ method:
self.data_bits = [8]  # Test only 8 data bits
self.parity_options = [None]  # Test only no parity
self.stop_bits = [1]  # Test only 1 stop bit
```

### Change Display Font
```python
# In the RGBDisplay.__init__ method:
self.font_width = 8   # Larger font
self.font_height = 10
```

### Add More Baud Rates
```python
# In the fallback method:
baud_rates = [
    9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600,
    1000000, 2000000  # Add custom baud rates
]
```

## Supported Displays

This program is designed for ST7735-based RGB displays with 128x160 resolution. Common compatible displays include:

- Adafruit 1.8" TFT Display
- Generic ST7735 RGB displays
- Other SPI RGB displays with similar specifications

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests! 