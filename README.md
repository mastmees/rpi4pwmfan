# 4-wire fan control service for Raspberry Pi 4 using hardware PWM

This code assumes that a 4-wire 5V fan is used, with PWM input
(normally blue wire) connected to GPIO12. Tach output (normally yellow wire)
is not used.

The code does not depend on any 3rd party libraries to make it easy to
install in 'externally managed' python config that Raspberry is using.

To install, first configure the system by adding

 dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4

into /boot/firmware/config.txt, then reboot. After that, run 

 sudo bash install.sh

This will set up a system service that runs the fancontrol.py and takes care
of restarting it in case of problems. You can check what the script is doing
by using

  systemctl status fancontrol

the 'Status: "temperature: 54.3 degC, fan speed 0%"' row is updated every 10
seconds. On startup, the script starts up the fan as audible indication that
everything is working as it should.

