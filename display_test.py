"""
Display test script for RGB display
Use this to verify your display connections and functionality
"""

import machine
import time
from machine import SPI, Pin
import framebuf

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
        self.width = 128
        self.height = 160
        
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
        
        # Create framebuffer
        self.buffer = bytearray(self.width * self.height * 2)  # 16-bit color
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.RGB565)
        
        # Clear display
        self.clear()
        
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
    
    def draw_rect(self, x, y, w, h, color=0xFFFF):
        """Draw rectangle"""
        self.fb.rect(x, y, w, h, color)
    
    def draw_filled_rect(self, x, y, w, h, color=0xFFFF):
        """Draw filled rectangle"""
        self.fb.fill_rect(x, y, w, h, color)
    
    def draw_circle(self, x0, y0, r, color=0xFFFF):
        """Draw circle using midpoint algorithm"""
        x = r
        y = 0
        d = 1 - r
        self.fb.pixel(x0 + x, y0 + y, color)
        self.fb.pixel(x0 - x, y0 + y, color)
        self.fb.pixel(x0 + x, y0 - y, color)
        self.fb.pixel(x0 - x, y0 - y, color)
        self.fb.pixel(x0 + y, y0 + x, color)
        self.fb.pixel(x0 - y, y0 + x, color)
        self.fb.pixel(x0 + y, y0 - x, color)
        self.fb.pixel(x0 - y, y0 - x, color)
        while x > y:
            y += 1
            if d <= 0:
                d = d + 2 * y + 1
            else:
                x -= 1
                d = d + 2 * (y - x) + 1
            if x < y:
                break
            self.fb.pixel(x0 + x, y0 + y, color)
            self.fb.pixel(x0 - x, y0 + y, color)
            self.fb.pixel(x0 + x, y0 - y, color)
            self.fb.pixel(x0 - x, y0 - y, color)
            self.fb.pixel(x0 + y, y0 + x, color)
            self.fb.pixel(x0 - y, y0 + x, color)
            self.fb.pixel(x0 + y, y0 - x, color)
            self.fb.pixel(x0 - y, y0 - x, color)

    def draw_filled_circle(self, x0, y0, r, color=0xFFFF):
        """Draw filled circle using midpoint algorithm"""
        x = r
        y = 0
        d = 1 - r
        self.fb.hline(x0 - r, y0, 2 * r + 1, color)
        while x > y:
            y += 1
            if d <= 0:
                d = d + 2 * y + 1
            else:
                x -= 1
                d = d + 2 * (y - x) + 1
            if x < y:
                break
            self.fb.hline(x0 - x, y0 + y, 2 * x + 1, color)
            self.fb.hline(x0 - x, y0 - y, 2 * x + 1, color)
            self.fb.hline(x0 - y, y0 + x, 2 * y + 1, color)
            self.fb.hline(x0 - y, y0 - x, 2 * y + 1, color)

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

def test_basic_display():
    """Test basic display functionality"""
    print("Testing RGB Display...")
    
    try:
        # Initialize display
        display = RGBDisplay(bl_pin=8)
        display.backlight_on()  # Ensure backlight is fully on
        print("Display initialized successfully")
        
        # Test 1: Clear screen
        display.clear(0x0000)  # Black
        print("Test 1: Clear screen (black)")
        time.sleep(1)
        
        # Test 2: Fill with white
        display.clear(0xFFFF)  # White
        print("Test 2: Fill screen (white)")
        time.sleep(1)
        
        # Test 3: Fill with red
        display.clear(0xF800)  # Red
        print("Test 3: Fill screen (red)")
        time.sleep(1)
        
        # Test 4: Fill with green
        display.clear(0x07E0)  # Green
        print("Test 4: Fill screen (green)")
        time.sleep(1)
        
        # Test 5: Fill with blue
        display.clear(0x001F)  # Blue
        print("Test 5: Fill screen (blue)")
        time.sleep(1)
        
        print("Basic color tests completed")
        
    except Exception as e:
        print(f"Error in basic display test: {e}")
        return False
    
    return True

def test_text_display():
    """Test text display functionality"""
    print("Testing text display...")
    
    try:
        display = RGBDisplay(bl_pin=8)
        display.backlight_on()  # Ensure backlight is fully on
        
        # Clear to black
        display.clear(0x0000)
        
        # Test text in different colors
        colors = [
            (0xFFFF, "White"),
            (0xF800, "Red"),
            (0x07E0, "Green"),
            (0x001F, "Blue"),
            (0xFFE0, "Yellow"),
            (0xF81F, "Magenta"),
            (0x07FF, "Cyan")
        ]
        
        for i, (color, name) in enumerate(colors):
            display.clear(0x0000)
            display.draw_text(f"Color: {name}", 10, 20, color)
            display.draw_text(f"Test {i+1}/7", 10, 40, color)
            display.draw_text("RGB Display", 10, 60, color)
            display.draw_text("Working!", 10, 80, color)
            display.update()
            print(f"Test {i+1}: {name} text")
            time.sleep(1)
        
        print("Text display tests completed")
        
    except Exception as e:
        print(f"Error in text display test: {e}")
        return False
    
    return True

def test_graphics():
    """Test graphics functionality"""
    print("Testing graphics...")
    
    try:
        display = RGBDisplay(bl_pin=8)
        display.backlight_on()  # Ensure backlight is fully on
        
        # Clear to black
        display.clear(0x0000)
        
        # Draw some shapes
        display.draw_rect(10, 10, 50, 30, 0xFFFF)  # White rectangle
        display.draw_filled_rect(70, 10, 50, 30, 0xF800)  # Red filled rectangle
        display.draw_circle(30, 80, 20, 0x07E0)  # Green circle
        display.draw_filled_circle(90, 80, 20, 0x001F)  # Blue filled circle
        
        # Add text
        display.draw_text("Graphics Test", 10, 120, 0xFFFF)
        display.draw_text("Shapes OK", 10, 140, 0xFFE0)
        display.update()
        print("Graphics test completed")
        time.sleep(3)
        
    except Exception as e:
        print(f"Error in graphics test: {e}")
        return False
    
    return True

def test_scrolling_text():
    """Test scrolling text functionality"""
    print("Testing scrolling text...")
    
    try:
        display = RGBDisplay(bl_pin=8)
        display.backlight_on()  # Ensure backlight is fully on
        
        # Clear to black
        display.clear(0x0000)
        
        # Test messages
        messages = [
            "Welcome to",
            "RP2040 Display",
            "Test Program",
            "Scrolling text",
            "is working!",
            "Line 6",
            "Line 7",
            "Line 8",
            "Line 9",
            "Line 10",
            "Line 11",
            "Line 12",
            "Line 13",
            "Line 14",
            "Line 15",
            "Line 16",
            "Line 17",
            "Line 18",
            "Line 19",
            "Line 20"
        ]
        
        # Simulate scrolling by showing different sets of lines
        for i in range(len(messages) - 10):
            display.clear(0x0000)
            for j in range(10):
                if i + j < len(messages):
                    y_pos = j * 8
                    display.draw_text(messages[i + j], 0, y_pos, 0xFFFF)
            display.update()
            print(f"Scrolling frame {i+1}")
            time.sleep(0.5)
        
        print("Scrolling text test completed")
        
    except Exception as e:
        print(f"Error in scrolling text test: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("RGB Display Test Program")
    print("=" * 30)
    
    tests = [
        ("Basic Display", test_basic_display),
        ("Text Display", test_text_display),
        ("Graphics", test_graphics),
        ("Scrolling Text", test_scrolling_text)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        if test_func():
            print(f"✅ {test_name} test PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} test FAILED")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Display is working correctly.")
    else:
        print("⚠️  Some tests failed. Check your connections.")

if __name__ == "__main__":
    main() 