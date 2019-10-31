#!/usr/bin/env python3

from gpiozero import LEDBoard, ButtonBoard, Button, CPUTemperature
from subprocess import check_call
from signal import pause
from time import sleep
from lcd import LCD_HD44780_I2C
from rgb import Color, RGBButton
from datetime import datetime
from pipelines import Pipelines, QueryResult, QueryResultStatus
from pprint import pprint


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

global pipes
global buildNumber
global activeEnvironment
global last_result
pipes = Pipelines()
buildNumber = ""
activeEnvironment = "Dev"
last_result = QueryResult()

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

def dev_deploy():
    deploy_question("Dev")
def stage_deploy():
    deploy_question("Stage")
def prod_deploy():
    deploy_question("Prod")

def deploy_question(environment):
    lcd.message = "{}\nDeploy to {}?".format(TITLE,environment)
    rgbmatrix.pulseButton(Color.RED, 1)
    rgbmatrix.unicornRing(25)
    bigButton.when_pressed = deploy

def deploy():
    # Find what we should be deploying.
    deploy_env = None
    if (toggle.prod.value):
        deploy_env = "Prod"
    elif (toggle.stage.value):
        deploy_env = "Staging"
    elif (toggle.dev.value):
        deploy_env = "Dev"
    else:
        return

    # Approve it.
    
    bigButton.when_pressed = None
    rgbmatrix.fillButton(Color.WHITE)
    rgbmatrix.stopRing()
    lcd.message = "{}Approving deployment to {}".format(TITLE,deploy_env)

    releaseApproval = pipes.approve(deploy_env)
    rgbmatrix.chaseRing(Color.BLUE, 1)
    if releaseApproval is not None:
        lcd.message = "{}{}\napproved to {}".format(TITLE,releaseApproval.release.name,releaseApproval.release_environment.name)

def toggle_release():
    print("Toggle down")
    if last_result is None:
        print("No last result available")
        return
    else:
        update_display(last_result)

def run_diagnostics():
    """ Diagnostic menu when Red button is held down """
    cpu = CPUTemperature()
    lcd.message = TITLE + \
        "\nIP:  " + get_ip() + \
        "\nCPU: " + str(round(cpu.temperature)) + chr(0xDF) + \
        "\nOff  Reset      Back" 
    switchLight.on()
    
    switch.red.wait_for_release()
    switch.red.when_held = None
    
    switch.red.when_pressed = shutdown
    switch.orange.when_pressed = reboot
 
    switch.blue.wait_for_press()
    
    # Blue light pressed - reset and drop out of diagnostics mode
    switchLight.off()
    switch.orange.when_pressed = None
    switch.red.when_pressed = None
    switch.red.when_held = run_diagnostics
    update_display(last_result)

def get_build_color(build_result):
    if (build_result == "succeeded"):
        return Color.GREEN
    elif (build_result == "failed"):
        return Color.RED
    elif (build_result == "canceled"):
        return Color.WHITE
    elif (build_result == "partiallySucceeded"):
        return Color.YELLOW
    return Color.OFF

def deploy_in_progress(result, environment):
    print("Deploy")
    rgbmatrix.fillButton(Color.WHITE)
    rgbmatrix.chaseRing(Color.BLUE, 1)
    lcd.message = "{}\n{}\n{}\nDeploying to {}...".format(TITLE,
        result.latest_build.definition.name,
        result.dev_release.name,
        environment)

def update_display(result):

    if results is None:
        return

    elif (toggle.dev.value == True):
        # Dev switch is up
        if (result.deploying_dev):
            # Dev deployment in progress
            deploy_in_progress(result, "Dev")

    elif (toggle.stage.value == True):
        # Stage switch is up
        if (result.deploying_stage):
            # Stage deployment in progress
            deploy_in_progress(result, "Staging")

    elif (toggle.prod.value == True):
        # Prod switch is up
        if (result.deploying_prod):
            # Prod deployment in progress
            deploy_in_progress(result, "Prod")

    elif (result.status == QueryResultStatus.BUILD_COMPLETE):
        rgbmatrix.fillButton(get_build_color(result.last_build.result))
        rgbmatrix.fillRing(Color.OFF)
        lcd.message = "{}\n{}\nBuild {}\n{}.".format(TITLE,
            result.latest_build.definition.name,
            result.latest_build.build_number,
            result.latest_build.result)

    elif (result.status == QueryResultStatus.BUILD_IN_PROGRESS):
        print("Build In Progress")
        rgbmatrix.pulseButton(get_build_color(result.last_build.result), 1)
        rgbmatrix.chaseRing(Color.BLUE, 1)
        lcd.message = "{}\n{}\nBuild {}\nin progress...".format(TITLE,
            result.latest_build.definition.name,
            result.latest_build.build_number)

    print(result.status)


def main():
    # Attach diagnotic menu to red button when held down
    switch.red.when_held = run_diagnostics

    toggle.dev.when_pressed = dev_deploy
    toggle.stage.when_pressed = stage_deploy
    toggle.prod.when_pressed = prod_deploy

    toggle.dev.when_released = toggle_release
    toggle.stage.when_released = toggle_release
    toggle.prod.when_released = toggle_release

    # Quick init sequence to show all is well
    lcd.message = TITLE + "\n\n\n" + get_ip()
    leds.blink(0.5,0.5,0,0,2,True)
    rgbmatrix.pulseButton(Color.RED, 1)
    rgbmatrix.unicornRing(25)
    lcd.message = TITLE

    # Set up build polling.
    # pipes = Pipelines()
    global last_result
    last_result = pipes.get_status()
    
    # Display loop
    while True:
        result = pipes.get_status()

        # Set the state of the approval toggle LED's
        toggleLight.dev.value = result.enable_dev
        toggleLight.stage.value = result.enable_stage
        toggleLight.prod.value = result.enable_prod

        if (result == last_result):
            # Nothing has changed - lets just wait a bit
            sleep(1)
        else:
            update_display(result)
            last_result = result    

main()
