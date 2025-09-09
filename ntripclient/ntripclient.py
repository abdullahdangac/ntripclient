#!/usr/bin/env python3

import time
import socket
import base64
import select
import threading

class NTRIPClient():
    def __init__(self, ntrip_server, ntrip_port, ntrip_version, mount_point, username, password):
        self.server_socket = None
        self.ntrip_server = ntrip_server
        self.ntrip_port = ntrip_port
        self.ntrip_version = ntrip_version
        self.mount_point = mount_point

        self.threads = []       # Thread list
        self.running = False    # Thread control flag

        self.NTRIP_VERSION = [
            "Ntrip/1.0",
            "Ntrip/2.0"
        ]

        self.SUCCESS_RESPONSES = [
            b"ICY 200 OK",
            b"HTTP/1.0 200 OK",
            b"HTTP/1.1 200 OK"
        ]

        if username is not None and password is not None:
            self.encoded_credentials = base64.b64encode('{}:{}'.format(username, password).encode('utf-8')).decode('utf-8')
        else:
            self.encoded_credentials = None

        if self.ntrip_version != None and self.ntrip_version != 0:
            if self.ntrip_version == 1:
                self.request_header = (
                    f"GET /{self.mount_point} HTTP/1.0\r\n"
                    f"Host: {self.ntrip_server}\r\n"
                    f"Ntrip-Version: {self.NTRIP_VERSION[0]}\r\n"
                )
            elif self.ntrip_version == 2:
                self.request_header = (
                    f"GET /{self.mount_point} HTTP/1.1\r\n"
                    f"Host: {self.ntrip_server}\r\n"
                    f"Ntrip-Version: {self.NTRIP_VERSION[1]}\r\n"
                )
            else:
                raise Exception("Error: Invalid NTRIP version")
        else:
            self.request_header = (
                f"GET /{self.mount_point} HTTP/1.0\r\n"
                f"Host: {self.ntrip_server}\r\n"
            )

        self.request_header += f"User-Agent: NTRIP Python Client/1.0\r\n"

        if self.encoded_credentials is not None:
            self.request_header += f"Authorization: Basic {self.encoded_credentials}\r\n"
        self.request_header += "\r\n"

    def connect(self):
        # Create a socket object that we will use to connect to the server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the server
        try:
            self.server_socket.connect((self.ntrip_server, self.ntrip_port))
        except Exception as e:
            print(f"[ERROR] Failed to connect socket to server at http://{self.ntrip_server}:{self.ntrip_port}")
            raise Exception(f"Exception: {e}")

        # Send the HTTP Request
        try:
            self.server_socket.sendall(self.request_header.encode('utf-8'))
        except:
            print(f"[ERROR] Failed to send request to server at http://{self.ntrip_server}:{self.ntrip_port}")
            raise Exception(f"Exception: {e}")

        # Get the response from the server
        try:
            response = self.server_socket.recv(1024)
            print(response.decode('utf-8'))
        except:
            print(f"Failed to get response from server at http://{self.ntrip_server}:{self.ntrip_port}")
            raise Exception(f"Exception: {e}")
        
        # Check the response and give some debug hints
        if any(success in response for success in self.SUCCESS_RESPONSES):
            print(f"Connected to http://{self.ntrip_server}:{self.ntrip_port}/{self.mount_point}\n")
        else:
            if b"SOURCETABLE 200 OK" in response:
                print("[ERROR] Received sourcetable response from the server. This probably means the mountpoint specified is not valid.")
            elif b"401" in response:
                print("[ERROR] Received unauthorized response from the server. Check your username, password and mountpoint to make sure they are correct.")
            else:
                print("[ERROR] Received unknown error from the server.")               

            raise Exception(f"[ERROR] Failed to connect to http://{self.ntrip_server}:{self.ntrip_port}/{self.mount_point}")

    def disconnect(self):
        try:
            if self.server_socket:
                self.server_socket.shutdown(socket.SHUT_RDWR)
                print(f"Socket is shutdown")
        except Exception as e:
            print('[ERROR] Encountered exception when shutting down the socket. This can likely be ignored.')
            print(f'Exception: {e}')

        try:
            if self.server_socket:
                self.server_socket.close()
                print(f"Socket is closed.")
        except Exception as e:
            print('[ERROR] Encountered exception when closing the socket. This can likely be ignored.')
            print(f'Exception: {e}')

    def send_nmea(self, nmea):
        try:
            self.server_socket.sendall(nmea.encode('utf-8') + b'\r\n')
        except Exception as e:
            print('[ERROR] Failed to send NMEA to NTRIP server')
            print(f'Exception: {e}')

    def receive_rtcm(self):
        # Check if there is any data available on the socket
        read_sockets, _, _ = select.select([self.server_socket], [], [], 0)
        if not read_sockets:
            #print('Socket is EMPTY')
            return []

        try:
            rtcm = self.server_socket.recv(1024)
            return rtcm
        except socket.timeout:
            print('[ERROR] Socket timeout')
            return None
        except Exception as e:
            print('[ERROR] Failed to receive RTCM from NTRIP server')
            print(f'Exception: {e}')
            return None

    # Starting both threads
    def start_threads(self, serial_port):
        self.running = True

        # NMEA thread
        t1 = threading.Thread(target=self._nmea_loop, args=(serial_port,), daemon=True)
        t1.start()
        self.threads.append(t1)

        # RTCM thread
        t2 = threading.Thread(target=self._rtcm_loop, args=(serial_port,), daemon=True)
        t2.start()
        self.threads.append(t2)

    # Sending NMEA thread
    def _nmea_loop(self, serial_port):
        while self.running:
            if serial_port.serial.in_waiting:
                nmea_line = serial_port.readline()
                if nmea_line.startswith('$GNGGA'):
                    self.send_nmea(nmea_line)
                    print(f"[NMEA Sent] {nmea_line}")
            time.sleep(0.01)

    # Getting RTCM thread
    def _rtcm_loop(self, serial_port):
        while self.running:
            data = self.receive_rtcm()
            if data:
                serial_port.write(data)
                print(f"[RTCM Received] {len(data)} bytes")
            time.sleep(0.01)
            
    # Stop threads
    def stop_threads(self):
        self.running = False
        for t in self.threads:
            t.join(timeout=1)  # Wait for threads to finish
        self.threads = []