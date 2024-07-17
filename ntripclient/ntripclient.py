#!/usr/bin/env python3

import socket
import base64
import select


class NTRIPClient():
    def __init__(self, ntrip_server, ntrip_port, ntrip_version, mount_point, username, password):
        self.server_socket = None
        self.ntrip_server = ntrip_server
        self.ntrip_port = ntrip_port
        self.ntrip_version = ntrip_version
        self.mount_point = mount_point

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
                raise Exception("Error: Invalid NTRIP version.")
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
            print(f"Failed to connect socket to server at http://{self.ntrip_server}:{self.ntrip_port}")
            raise Exception(f"Exception: {e}")

        # Send the HTTP Request
        try:
            self.server_socket.sendall(self.request_header.encode('utf-8'))
        except:
            print(f"Failed to send request to server at http://{self.ntrip_server}:{self.ntrip_port}")
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
            print(f"Connected to http://{self.ntrip_server}:{self.ntrip_port}/{self.mount_point}")
        else:
            if b"SOURCETABLE 200 OK" in response:
                print("Received sourcetable response from the server. This probably means the mountpoint specified is not valid")
            elif b"401" in response:
                print("Received unauthorized response from the server. Check your username, password and mountpoint to make sure they are correct.")
            else:
                print("Received unknown error from the server.")               

            raise Exception(f"Failed to connect to http://{self.ntrip_server}:{self.ntrip_port}/{self.mount_point}")

    def disconnect(self):
        try:
            if self.server_socket:
                self.server_socket.shutdown(socket.SHUT_RDWR)
                print(f"Socket is shutdown.")
        except Exception as e:
            print('Encountered exception when shutting down the socket. This can likely be ignored')
            print(f'Exception: {e}')

        try:
            if self.server_socket:
                self.server_socket.close()
                print(f"Socket is closed.")
        except Exception as e:
            print('Encountered exception when closing the socket. This can likely be ignored')
            print(f'Exception: {e}')

    def send_nmea(self, nmea):
        try:
            self.server_socket.sendall(nmea.encode('utf-8') + b'\r\n')
        except Exception as e:
            print('Failed to send NMEA to NTRIP server')
            print(f'Exception: {e}')

    def receive_rtcm(self):
        # Check if there is any data available on the socket
        read_sockets, _, _ = select.select([self.server_socket], [], [], 0)
        if not read_sockets:
            print('Socket is EMPTY')
            return []

        try:
            rtcm = self.server_socket.recv(1024)
            return rtcm
        except socket.timeout:
            print('Socket timeout.')
            return None
        except Exception as e:
            print('Failed to receive RTCM from NTRIP server')
            print(f'Exception: {e}')
            return None