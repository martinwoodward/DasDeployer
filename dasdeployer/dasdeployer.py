#!/usr/bin/env python3

from gpiozero import LEDBoard, ButtonBoard, Button, CPUTemperature
from subprocess import check_call
from signal import pause
from time import sleep
from lcd import LCD_HD44780_I2C
from rgb import Color, RGBButton
from datetime import datetime

import socket

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/martinwoodward/DasDeployer.git"

TITLE = ">>> Das Deployer <<<"

# Define controls
switchLight = LEDBoard(red=4, orange=27, green=13, blue=26, pwm=True)
switch = ButtonBoard(red=6, orange=5, green=25, blue=24, hold_time=5)
toggleLight = LEDBoard(dev=12, stage=20, prod=19)
toggle = ButtonBoard(dev=16, stage=23, prod=22, pull_up=False)
leds = LEDBoard(switchLight, toggleLight)
lcd = LCD_HD44780_I2C()
rgbmatrix = RGBButton()
bigButton = Button(17)
buildNumber = ""
activeEnvironment = "Dev"

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
    check_call(['sudo', 'poweroff'])

def reboot():
    lcd.message = "Das rebooting..."
    leds.off()
    check_call(['sudo', 'reboot'])

def demo_release_toggle():
    lcd.message = "{}\nContosoAir {}\nBuild Successful.".format(TITLE,buildNumber)
    rgbmatrix.fillButton(Color.GREEN)
    rgbmatrix.stopRing()
    bigButton.when_pressed = None

def demo_dev_deploy():
    demo_deploy_question("Dev")
def demo_stage_deploy():
    demo_deploy_question("Staging")
def demo_prod_deploy():
    demo_deploy_question("Prod")

def demo_deploy_question(location):
    activeEnvironment = location
    lcd.message = "{}\nContosoAir\n{}\nDeploy to {}?".format(TITLE,buildNumber,activeEnvironment)
    rgbmatrix.pulseButton(Color.RED, 1)
    rgbmatrix.unicornRing(25)
    bigButton.when_pressed = demo_deploy
    return activeEnvironment

def demo_deploy():
    bigButton.when_pressed = None
    rgbmatrix.fillButton(Color.WHITE)
    rgbmatrix.chaseRing(Color.BLUE, 1)
    lcd.message = "{}\nContosoAir\n{}\nDeploying to {}...".format(TITLE,buildNumber,activeEnvironment)
    if activeEnvironment == "Dev":
        toggle.dev.when_released = None
    elif activeEnvironment == "Staging":
        toggle.stage.when_released = None
    elif activeEnvironment == "Prod":
        toggle.prod.when_released = None
    sleep(10)
    rgbmatrix.fillButton(Color.GREEN)
    rgbmatrix.stopRing()
    lcd.message = "{}\nContosoAir {}\nDeploy Successful.".format(TITLE,buildNumber)
    if activeEnvironment == "Dev":
        toggleLight.dev.off()
    elif activeEnvironment == "Staging":
        toggleLight.stage.off()
    elif activeEnvironment == "Prod":
        toggleLight.prod.off()

def demo():
    # Demo mode
    leds.off()
    rgbmatrix.off()    
    switch.green.when_pressed = None
    switch.orange.when_pressed = None
    switch.red.when_pressed = None
    switch.red.when_held = run_diagnostics
    lcd.message = TITLE

    sleep(3)
    rgbmatrix.fillButton(Color.GREEN)
    sleep(3)

    buildNumber = "{:%Y%m%d.%M}".format(datetime.now())

    # Building
    lcd.message = "{}\nBuilding ContosoAir\n\n{}...".format(TITLE,buildNumber) 
    rgbmatrix.pulseButton(Color.GREEN, 1)
    rgbmatrix.chaseRing(Color.BLUE, 1)
    sleep(10)

    # Good build
    lcd.message = "{}\nContosoAir\n{}\nBuild Successful.".format(TITLE,buildNumber)
    rgbmatrix.fillButton(Color.GREEN)
    rgbmatrix.pulseRing(Color.WHITE, 1)
    sleep(2)
    rgbmatrix.stopRing()
    
    toggle.dev.when_pressed = demo_dev_deploy
    toggle.stage.when_pressed = demo_stage_deploy
    toggle.prod.when_pressed = demo_prod_deploy
 
    toggle.dev.when_released = demo_release_toggle
    toggle.stage.when_released = demo_release_toggle
    toggle.prod.when_released = demo_release_toggle

    sleep(5)
    toggleLight.dev.on()
    sleep(1)
    toggleLight.stage.on()
    sleep(1)
    toggleLight.prod.on()

def run_diagnostics():
    """ Diagnostic menu when Red button is held down """
    cpu = CPUTemperature()
    lcd.message = TITLE + \
        "\nIP:  " + get_ip() + \
        "\nCPU: " + str(round(cpu.temperature)) + chr(0xDF) + \
        "\nOff        Demo Back" 
    switchLight.on()
    
    switch.red.wait_for_release()
    switch.red.when_held = None
    
    switch.red.when_pressed = shutdown
    switch.orange.when_pressed = reboot
 
    switch.blue.wait_for_press()

    switchLight.off()
    
    switch.orange.when_pressed = None
    switch.red.when_pressed = None
    switch.red.when_held = run_diagnostics
    lcd.message = TITLE

def main():
    # Attach diagnotic menu to red button when held down
    switch.red.when_held = run_diagnostics

    # Quick init sequence to show all is well
    lcd.message = TITLE + "\n\n\n" + get_ip()
    leds.blink(0.5,0.5,0,0,2,True)
    rgbmatrix.pulseButton(Color.RED, 1)
    rgbmatrix.unicornRing(25)
    sleep(4)
    rgbmatrix.off()

    lcd.message = TITLE

    pause()

main()
