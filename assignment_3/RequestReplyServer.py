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
    unique_request_id = "" # last id was send. Used to match the most recent received one
    udp_ip = ""
    udp_port = ""
    message = ""
    local_port = ""

    def __init__(self, udp_ip, udp_port, message, local_port, timeout):
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.message = message
        self.local_port = local_port
        self.timeout = timeout

    def send(self):
        # Prepare the header as A1
        self.unique_request_id = bytearray(16)
        self.unique_request_id += binascii.hexlify(
            socket.inet_aton(socket.gethostbyname(socket.gethostname()))
        ).upper()  # IP 4 bytes
        self.unique_request_id += struct.unpack("xH", self.local_port)  # Port 2 bytes
        self.unique_request_id += struct.unpack("xH", time.localtime()) # Local time 2 bytes

        self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id + self.message)

    def receive(self):
        resend_counter = 1
        while True:

            data = self.udp_obj.receive(self.udp_port + 10, self.timeout * self.timeout)
            received_header = data[0:15]
            data = data[16:]
            if self.unique_request_id == received_header:
                return data


            self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id + self.message)


