#!/usr/bin/env python3

import argparse
from lcd import LCD_HD44780_I2C

parser = argparse.ArgumentParser(
    description='Write a message to the LCD matrix display.', 
    epilog='Example: ./writelcd.py $\'Hello\\nWorld!\'')
parser.add_argument('message', help='Text to write to the display')
parser.add_argument('--displayOff', dest='display', action='store_false', default=True, help='Turn off the display')

args = parser.parse_args()

lcd = LCD_HD44780_I2C()
if (args.display):
    lcd.message = args.message
else:
    lcd.clear(False)




