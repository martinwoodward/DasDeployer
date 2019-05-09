#!/bin/sh

### BEGIN INIT INFO
# Provides:          bootinfo
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Show status on LCD during boot and shut down
# Description:       Update the LCD on boot and turn off the display on shut down
### END INIT INFO

case "$1" in
  start)
    /home/pi/DasDeployer/dasdeployer/writelcd.py '>>> Das Deployer <<<Initialising...'
    ;;
  stop)
    /home/pi/DasDeployer/dasdeployer/writelcd.py --displayOff 'Safe to power off'
    ;;
  *)
    echo "Usage: /etc/init.d/bootinfo {start|stop}"
    exit 1
    ;;
esac

exit 0