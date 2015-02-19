__author__ = 'Owner'
# To-Do do whatever we did in assignment 1
import socket
import time
import binascii
import struct
import udpSendRecieve


class RequestReplyServer:
    udp_obj = udpSendRecieve.UDPNetwork()
    timeout = .1  # 100 ms by default unless changed by constructor
    # For retransmission
    unique_request_id  = bytearray(16) # last id was send. Used to match the most recent received one
    # udp_ip = ""
    # udp_port = ""
    # message = ""
    # local_port = ""

    def __init__(self,  timeout):
        # self.udp_ip = udp_ip
        # self.udp_port = udp_port
        # self.message = message
        # self.local_port = local_port
        self.timeout = timeout

    def send(self, udp_ip, udp_port, message):
        # Prepare the header as A1
        self.udp_obj.send(udp_ip, udp_port + 1000, self.unique_request_id + message)

    def receive(self, udp_port):
        while True:
            data = self.udp_obj.receive(udp_port, self.timeout)
            received_header = data[0:15]
            self.unique_request_id = received_header
            data = data[16:]
            return received_header, data


