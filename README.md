[![Build Status](https://dev.azure.com/martin/DasDeployer/_apis/build/status/martinwoodward.DasDeployer?branchName=master&label=DasBuild)](https://dev.azure.com/martin/DasDeployer/_build/latest?definitionId=43&branchName=master)

# DasDeployer

Raspberry Pi powered manual release approval gate for Azure Pipelines. Mit viele blinkenlighten.

![DasDeployer](images/dasdeployer-hero.png?raw=true "Das Deployer")

I did a short talk about this project at Microsoft Ignite 2019.
 - [Video](https://myignite.techcommunity.microsoft.com/sessions/83984)
 - [Slides](https://1drv.ms/p/s!AnoZDWDiiqDHxsEOiek9n2gWs0enNA)

## Component List
 - Gun Metal Grey Aluminium Flight Case (340 x 240 x 120mm) [[UK]](https://amzn.to/2v9PrQS) [[US Similar Size]](https://amzn.to/34DP5BR)
 - Raspberry Pi 3 Model B+ [[UK]](https://amzn.to/2KLshuM) [[US]](https://amzn.to/33wm6Q8)
 - SD card containing [Raspbian](https://www.raspberrypi.org/downloads/raspbian/) [[UK]](https://amzn.to/2UqUDKE) [[US]](https://amzn.to/34HCTAc)
 - 3mm Black Carbon Fibre Effect ABS Sheet (420mm x 297mm / A3) [[UK]](https://amzn.to/2XfYHPp) [[US]](https://amzn.to/34F52rj)
 - 4 Inch / 100mm Big Dome Illuminated Push Button with Microswitch (White) [[UK]](https://amzn.to/2KG42Ox) [[US]](https://amzn.to/2Q0bIMz)
 - HD44780 20x4 Blue Screen LCD Module with I2C Serial Interface Adapter [[UK]](https://amzn.to/2V8PiM6) [[US]](https://amzn.to/2JXyalO)
 - Illuminated Square Momentary Push Buttons (4 needed from pack of 5) [[UK]](https://amzn.to/2KJMPEa) [[US]](https://amzn.to/2NuF2cB)
 - 112mm 32 WS2812B 5050 RGB LED Ring (Adafruit Neopixel compatible) [[UK]](https://amzn.to/2V5ClD0) [[US]] (https://amzn.to/2WZMQGn)
 - 32mm 8 WS2812B 5050 RGB LED Ring (Adafruit Neopixel compatible) [[UK]](https://amzn.to/2KKgZqD) [[US]](https://amzn.to/2WZMQGn)
 - Blue Toggle Switches with face plate [[UK]](https://amzn.to/2VQ2gvt) [[US]](https://amzn.to/2K0xgoG)
 - Panel Mount Male IEC320 C8 Power Socket [[UK]](https://amzn.to/2VOCcAW) [[US]](https://amzn.to/2PYfgiH)
 - Panel Mount Ethernet Extension Cable [[UK]](https://amzn.to/2vdWHLv) [[US]](https://amzn.to/34KbL3x)
 - Dual USB3.0 Square Flush Mount [[UK]](https://amzn.to/2v5Q4el) [[US]](https://amzn.to/36J7Gy5)
 - 5V/12V/24V Switching Power Supply for Arcade Machine [[UK]](https://amzn.to/2VPowpo) [[US]](https://amzn.to/33u6cpF)
 - Terminal Block Breakout Module for Raspberry Pi [[UK]](https://amzn.to/2VUm4Ox) [[US]](https://amzn.to/2NuFGH3)
 - N-Channel Power MOSFET (4 needed) [[UK]](https://amzn.to/2KHKY2q) [[US]](https://amzn.to/2pRd69O)
 - 8-Channel IIC I2C Logic Level Converter [[UK]](https://amzn.to/2VEK0IH) [[US]](https://amzn.to/33sXGqT)
 - Assorting wiring, breadboard, spade connectors, Torx security screws, PCB spacers, scrap wood etc
 
## Equipment
 - Dremel
 - Soldering Iron
 - Hot melt glue gun
 - Screwdrivers
 - Superglue
 - Drill, bits (including hole cutting accessories)

## RPi GPIO Assignment
The following lists the GPIO port assignments for the Raspberry Pi.

| RPi   | Description   |
| ----- | ------------- |
| IO17  | Main Button Switch |
| IO21  | RGB Data In |
| IO2 (SDA)   | LCD SDA |
| IO3 (SCL)   | LCD SCL |
| IO4   | Red Button LED |
| IO6   | Red Button Switch |
| IO27  | Orange Button LED |
| IO5   | Orange Button Switch |
| IO13  | Green Button LED |
| IO25  | Green Button Switch |
| IO26  | Blue Button LED |
| IO24  | Blue Button Switch |
| IO12  | Dev Toggle LED |
| IO16  | Dev Toggle Switch |
| IO20  | Stage Toggle LED |
| IO23  | Stage Toggle Switch |
| IO19  | Prod Toggle LED|
| IO22  | Prod Toggle Switch |

## Hardware Build
TODO

## Software Installation
1. Download the latest Raspian image to a Micro-SD Card, create a file in the root of the image called 'ssh' to enable ssh access in a headless environment. SSH to server and do apt-get update/upgrade etc
2. Change the password for the default pi user, everything else assumes you are running as that user.
3. Enable i2c using raspi-config
4. Install pre-requisites (TODO: list these but ideally script out this part)
5. git clone this repo into the /home/pi directory.

Installing the service
We want the `dasdeployer` service to run after the network comes up on the Raspberry Pi.  Therefore we use systemd to allow us to do that.  I'm an old fashioned SysV init.d type of person and systemd was new to me therefore the following resources were very helpful:

 - https://raspberrypi.stackexchange.com/a/79033
 - https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units
 - https://www.digitalocean.com/community/tutorials/understanding-systemd-units-and-unit-files

Basically I entered the following commands:

```
chmod a+rx /home/pi/DasDeployer/scripts/dasdeployer.sh
chmod a+rx /home/pi/DasDeployer/dasdeployer/dasdeployer.py
sudo systemctl edit --force --full dasdeployer.service
```

and then set the service configuration to be as follows

```
[Unit]
Description=Das Deployer
Wants=network-online.target
After=network-online.target

[Service]
Type=forking
User=root
WorkingDirectory=/home/pi/DasDeployer/scripts
ExecStart=/home/pi/DasDeployer/scripts/dasdeployer.sh start

[Install]
WantedBy=multi-user.target
```

Then I enabled and started the service, followed by a quick reboot to make sure everything worked correctly on initial start.

```
sudo systemctl enable dasdeployer.service
sudo systemctl start dasdeployer.service
sudo shutdown -r now
```


