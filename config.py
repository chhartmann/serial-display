"""
Configuration file for serial auto-configuration
Modify these settings to customize the behavior
"""

# UART Configuration
UART_ID = 0          # UART interface ID (0 or 1)
TX_PIN = 0           # TX pin number
RX_PIN = 1           # RX pin number

# LED Configuration
LED_PIN = 25         # Built-in LED pin

# Display Configuration
DISPLAY_SPI_ID = 0   # SPI interface ID
DISPLAY_DC_PIN = 8   # Data/Command pin
DISPLAY_CS_PIN = 9   # Chip Select pin
DISPLAY_RST_PIN = 12 # Reset pin
DISPLAY_WIDTH = 128  # Display width in pixels
DISPLAY_HEIGHT = 160 # Display height in pixels
DISPLAY_FONT_WIDTH = 6   # Font width in pixels
DISPLAY_FONT_HEIGHT = 8  # Font height in pixels

# Baud Rate Detection Configuration
DETECTION_RX_PIN = 1     # RX pin for pulse measurement
DETECTION_MIN_SAMPLES = 10   # Minimum samples for detection
DETECTION_MAX_SAMPLES = 50   # Maximum samples to collect
DETECTION_TIMEOUT_MS = 5000  # Timeout for detection in milliseconds
DETECTION_TOLERANCE = 0.1    # Tolerance for baud rate matching (10%)
DETECTION_MIN_PULSE_US = 100     # Minimum pulse width in microseconds
DETECTION_MAX_PULSE_US = 1000000 # Maximum pulse width in microseconds

# Standard baud rates for detection matching
STANDARD_BAUD_RATES = [
    9600,      # Common for older devices
    19200,     # Legacy devices
    38400,     # Legacy devices
    57600,     # Legacy devices
    115200,    # Most common
    230400,    # High speed
    460800,    # High speed
    921600     # Very high speed
]

# Data bit configurations
DATA_BITS = [7, 8]

# Parity settings (None = no parity, 0 = even, 1 = odd)
PARITY_OPTIONS = [None, 0, 1]

# Stop bit configurations
STOP_BITS = [1, 2]

# Testing Configuration
TEST_TIMEOUT = 1000      # Timeout in milliseconds for each test
MIN_DATA_LENGTH = 10     # Minimum data length to consider valid
PRINTABLE_THRESHOLD = 0.5  # Minimum percentage of printable characters (0.0 to 1.0)

# Monitoring Configuration
MONITOR_TIMEOUT = 1000   # Timeout for monitoring mode
GC_INTERVAL = 1000       # Garbage collection interval (ms)

# Debug Configuration
DEBUG_MODE = False       # Enable debug output
SHOW_HEX_DATA = True     # Show hex data for non-printable characters

# Performance Configuration
FAST_MODE = False        # Skip some configurations for faster testing
# If FAST_MODE is True, only test these configurations:
FAST_BAUD_RATES = [9600, 115200]
FAST_DATA_BITS = [8]
FAST_PARITY_OPTIONS = [None]
FAST_STOP_BITS = [1]

# Detection Mode Configuration
USE_BAUD_DETECTION = True    # Enable baud rate detection
FALLBACK_TO_TRADITIONAL = True  # Fall back to traditional method if detection fails 