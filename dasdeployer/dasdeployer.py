#!/usr/bin/env python3

from gpiozero import LEDBoard
from signal import pause
from time import sleep
from lcd import LCD_HD44780_I2C
import time
import smbus
import socket

# Define controls
switchLight = LEDBoard(red=4, orange=27, green=13, blue=26, pwm=True)
toggleLight = LEDBoard(dev=12, stage=20, prod=19)
leds = LEDBoard(switchLight, toggleLight)
lcd = LCD_HD44780_I2C()

## Nifty get_ip function from Jamieson Becker https://stackoverflow.com/a/28950776
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# Quick init sequence to test all is well
leds.blink(0.5,0.5,0,0,1,False)

lcd.message = ">>> Das Deployer <<<\n\n\n" + get_ip()

# Pulse button lights (software PWM)
switchLight.pulse(0.5, 0.5, 3, True)

pause()
