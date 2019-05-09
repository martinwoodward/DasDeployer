"""
`dasdeployer.lcd`
====================================================

Generic HD44780 based lcd matrix display with a I2C character LCD backpack

* Author(s): Martin Woodward

Implementation Notes
--------------------
Magic numbers cribbed from lcd_i2c.py written by Matt Hawkins 
<https://www.raspberrypi-spy.co.uk/2015/05/using-an-i2c-enabled-lcd-screen-with-the-raspberry-pi/>

For an explaination of the magic numbers and character code lookup table see SparkFun
<https://www.sparkfun.com/datasheets/LCD/HD44780.pdf>

Code inspired by Adafruit's excellent CircuitPython CharLCD library
<https://github.com/adafruit/Adafruit_CircuitPython_CharLCD/blob/master/adafruit_character_lcd/character_lcd.py>

**Hardware:**

"* `20x4 Character LCD with HD44780 controller via IIC/I2C Serial Interface Adapter <https://amzn.to/2JqRpF5>`_"

**Software and Dependencies:**

* python3-smbus, i2c-tools

"""
import smbus
import time

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/martinwoodward/DasDeployer.git"

#LCD Ram addresses for each line
_LCD_ROW_OFFSETS = (0x80, 0xC0, 0x94, 0xD4)

_LCD_BACKLIGHT  = 0x08  # 0x08 On, 0x00 Off

_ENABLE = 0b00000100 # Enable bit

# Timing constants
_DELAY = 0.0003

class LCD_HD44780_I2C:
    def __init__(self, cols=20, rows=4, address=0x27):
        self.cols = cols
        self.rows = rows
        self.address = address

        # Initialise the bus
        self.bus = smbus.SMBus(1) # Modern Pi uses 1, old Pi's (Rev 1) use 0

        # Use the bus to initialise the display using some magic bits
        self._write8(0x33) # 110011 Initialise
        self._write8(0x32) # 110010 Initialise
        self._write8(0x06) # 000110 Cursor move direction
        self._write8(0x0C) # 001100 Display On,Cursor Off, Blink Off 
        self._write8(0x28) # 101000 Data length, number of lines, font size
        self.clear()
        time.sleep(_DELAY)

    def _write8(self, bits, char_mode=False, backlight=_LCD_BACKLIGHT):
        """ Send a byte to the data pins.
        
        Parameters
        ----------
        bits : int
            The data to send
        char_mode : bool
            False for a command, True for character data
        backlight : int
            0 for backlight off, 0x08 for on
        """
        bits_high = char_mode | (bits & 0xF0) | backlight
        bits_low = char_mode | ((bits<<4) & 0xF0) | backlight

        # High nibble
        self.bus.write_byte(self.address, bits_high)
        self._pulse_enable(bits_high)

        # Low nibble
        self.bus.write_byte(self.address, bits_low)
        self._pulse_enable(bits_low)

    def _pulse_enable(self, bits):
        # Toggle enable
        time.sleep(_DELAY)
        self.bus.write_byte(self.address, (bits | _ENABLE))
        time.sleep(0.0003)
        self.bus.write_byte(self.address,(bits & ~_ENABLE))
        time.sleep(_DELAY)
        
    def printLine(self, message, row):
        # Send string to display
        if (0 <= row < self.rows):
            message = message.ljust(self.cols," ")
            self._write8(_LCD_ROW_OFFSETS[row])
            for i in range(self.cols):
                self._write8(ord(message[i]), True)
    
    @property
    def message(self):
        """Display a string of text on the character LCD.
        """
        return self._message

    @message.setter
    def message(self, message):
        self._message = message
        row = 0
        col = 0
        line = ""
        # iterate through each character
        for character in message:
            # If character is \n or we have ran out or room, go to next line
            if (character == '\n') or (col >= self.cols):
                self.printLine(line, row)
                row += 1
                col = 0
                if character == '\n':
                    character = ''
                line = character
            else:
                # Add character to current line
                line += character
                col += 1
        self.printLine(line, row)
        # Fill the remainer of screen with empty characters
        for i in range(row + 1, self.rows + 1):
            self.printLine("",i)

    def clear(self, backlight=True):
        if (backlight):
            self._write8(0x01) # 000001 Clear display
        else:
            self._write8(0x01, False, 0) # Clear display and turn off backlight
        


