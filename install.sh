#!/bin/bash
systemctl stop fancontrol
adduser daemon gpio
cp fancontrol.py /usr/bin
cp fancontrol.service /etc/systemd/system
systemctl daemon-reload
systemctl enable fancontrol
systemctl start fancontrol
systemctl status fancontrol
