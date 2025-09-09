#!/usr/bin/env python3

import serial


class SerialCom:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.serial = None
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        
    def open(self):
        try:
            self.serial = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
            if self.serial.is_open:
                print(f"Serial port {self.port} is opened at {self.baudrate} baudrate\n")
        except serial.SerialException as e:
            raise Exception(f"Error opening serial port: {e}")

    def close(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            print(f"Serial port {self.port} is closed.")

    def write(self, data):
        if self.serial and self.serial.is_open:
            try:
                if (type(data) == 'str'):
                    self.serial.write(data.encode('utf-8'))
                else:
                    self.serial.write(data)
            except serial.SerialException as e:
                print(f"Error sending data: {e}")

    def read(self, size=1):
        if self.serial and self.serial.is_open:
            try:
                data = self.serial.read(size)
                return data
            except serial.SerialException as e:
                print(f"Error receiving data: {e}")
                return None

    def readline(self):
        if self.serial and self.serial.is_open:
            try:
                data = self.serial.readline().decode('utf-8').strip()
                return data
            except serial.SerialException as e:
                print(f"Error receiving data: {e}")
                return None