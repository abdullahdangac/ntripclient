#!/usr/bin/env python3

import time
import argparse
from serialcom import SerialCom
from ntripclient import NTRIPClient


def main(serial_port, serial_baudrate, serial_timeout, ntrip_server, ntrip_port, ntrip_version, mountpoint, username, password):
    # Set serial
    gnss_serial = SerialCom(serial_port, serial_baudrate, timeout=serial_timeout)

    # Set NTRIP client
    ntripclient = NTRIPClient(ntrip_server, ntrip_port, ntrip_version, mountpoint, username, password)

    try:
        gnss_serial.open()
        ntripclient.connect()
        ntripclient.start_threads(gnss_serial)

        # Main thread loop
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")

    except KeyboardInterrupt:
        print(f"KeyboardInterrupt")

    finally:
        if (ntripclient.server_socket):
            ntripclient.stop_threads()
        
        if (gnss_serial.serial and gnss_serial.serial.is_open):
            gnss_serial.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    
    parser.add_argument('-p', '--serial_port', type=str, required=True, help='Serial port name')
    parser.add_argument('-b', '--serial_baudrate', type=int, required=True, help='Serial port baudrate')
    parser.add_argument('-t', '--serial_timeout', type=int, required=False, help='Serial port baudrate')
    parser.add_argument('-S', '--ntrip_server', type=str, required=True, help='NTRIP server')
    parser.add_argument('-P', '--ntrip_port', type=int, required=True, help='NTRIP server port')
    parser.add_argument('-V', '--ntrip_version', type=int, required=True, help='NTRIP version')
    parser.add_argument('-M', '--mountpoint', type=str, required=True, help='Mountpoint')
    parser.add_argument('-U', '--username', type=str, required=True, help='Username')
    parser.add_argument('-W', '--password', type=str, required=True, help='Password')

    args = parser.parse_args()
    main(args.serial_port, 
         args.serial_baudrate, 
         args.serial_timeout, 
         args.ntrip_server, 
         args.ntrip_port, 
         args.ntrip_version, 
         args.mountpoint, 
         args.username, 
         args.password, 
    )