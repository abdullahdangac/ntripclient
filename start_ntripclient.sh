#!/bin/bash

#----------------------------------------------------------
#                     CONFIGURATIONS
#----------------------------------------------------------
# Serial Communication Configurations
#----------------------------------------------------------
SERIAL_PORT="/dev/ttyUSB0"       # Serial port name of the GNSS receiver
SERIAL_BAUDRATE=115200           # Serial baudrate of the GNSS receiver
SERIAL_TIMEOUT=1                 # Serial timeout
#----------------------------------------------------------
# NTRIP Client Configurations
#----------------------------------------------------------
NTRIP_SERVER="www.euref-ip.net"  # NTRIP server/caster IP address
NTRIP_PORT=2101                  # NTRIP server/caster port
NTRIP_VERSION="Ntrip/1.0"        # NTRIP version (use 1 for Ntrip/1.0 and use 2 for Ntrip/2.0)
MOUNTPOINT="M0uNtp0iNt"          # NTRIP mountpoint
USERNAME="username"              # NTRIP server/caster username
PASSWORD="password"              # NTRIP server/caster password
#----------------------------------------------------------


python3 ntripclient/__main__.py \
    -p $SERIAL_PORT \
    -b $SERIAL_BAUDRATE \
    -t $SERIAL_TIMEOUT \
    -S $NTRIP_SERVER \
    -P $NTRIP_PORT \
    -V $NTRIP_VERSION \
    -M $MOUNTPOINT \
    -U $USERNAME \
    -W $PASSWORD