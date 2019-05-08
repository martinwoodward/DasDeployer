#!/usr/bin/env python3

from gpiozero import LEDBoard, ButtonBoard, Button, CPUTemperature
from subprocess import check_call
from signal import pause
from time import sleep
from lcd import LCD_HD44780_I2C
import socket

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/martinwoodward/DasDeployer.git"

# Define controls
switchLight = LEDBoard(red=4, orange=27, green=13, blue=26, pwm=True)
switch = ButtonBoard(red=6, orange=5, green=25, blue=24, hold_time=5)
toggleLight = LEDBoard(dev=12, stage=20, prod=19)
toggle = ButtonBoard(dev=16, stage=23, prod=22, pull_up=False)
leds = LEDBoard(switchLight, toggleLight)
lcd = LCD_HD44780_I2C()
bigButton = Button(17)

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

def shutdown():
    lcd.message = "Switching off..."
    sleep(3)
    leds.off()
    lcd.clear(False)
    check_call(['sudo', 'poweroff'])

def reboot():
    lcd.message = "Das rebooting..."
    leds.off()
    check_call(['sudo', 'reboot'])

def run_diagnostics():
    """ Diagnostic menu when Red button is held down """
    cpu = CPUTemperature()
    lcd.message = ">>> Das Deployer <<<" + \
        "\nIP:  " + get_ip() + \
        "\nCPU: " + str(round(cpu.temperature)) + chr(0xDF) + \
        "\nOff  Reset      Back" 
    switch.red.wait_for_release()
    switch.red.when_held = None
    switch.red.when_pressed = shutdown
    switch.orange.when_pressed = reboot
    switch.blue.wait_for_press()
    switch.red.when_pressed = None
    switch.red.when_held = run_diagnostics
    lcd.message = ">>> Das Deployer <<<"

# Attach diagnotic menu to red button when held down
switch.red.when_held = run_diagnostics


# Quick init sequence to test all is well
lcd.message = ">>> Das Deployer <<<\n\n\n" + get_ip()
leds.blink(0.5,0.5,0,0,2,False)

lcd.message = ">>> Das Deployer <<<"


pause()
