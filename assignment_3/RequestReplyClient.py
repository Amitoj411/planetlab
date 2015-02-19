__author__ = 'Owner'
# To-Do do whatever we did in assignment 1
import socket
import time
import binascii
import struct
import udpSendRecieve


class RequestReplyClient:
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
        self.unique_request_id.append( binascii.hexlify(
            socket.inet_aton(socket.gethostbyname(socket.gethostname()))
        ).upper()
        )# IP 4 bytes
        self.unique_request_id.append(struct.unpack("xH", struct.pack("i", int(self.local_port))))  # Port 2 bytes
        self.unique_request_id.append(struct.unpack("xH", struct.pack("i", int(time.strftime("%M")))))  # Local time 2 bytes

        self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id + self.message)

    def receive(self):
        resend_counter = 1
        while resend_counter <= 3:
            try:
                data = self.udp_obj.receive(self.udp_port + 1000, self.timeout * self.timeout)
                received_header = data[0:15]
                data = data[16:]
                if self.unique_request_id == received_header:
                    return data
            except socket.error:
                resend_counter += 1
                self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id + self.message)
                print "Timeout 100 ms. Sending again, trail: " + str(resend_counter)

        return -1


