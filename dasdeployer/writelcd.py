#!/usr/bin/env python3

import argparse
from lcd import LCD_HD44780_I2C

parser = argparse.ArgumentParser(description='Write a message to the LCD matrix display.')
parser.add_argument('message', type=str,
                   help='Text to write to the display')

args = parser.parse_args()

lcd = LCD_HD44780_I2C()
lcd.message = args.message


