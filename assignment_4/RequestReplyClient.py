__author__ = 'Owner'
# To-Do do whatever we did in assignment 1
import socket
import time
import binascii
import struct
import udpSendRecieve
from array import array


class RequestReplyClient:
    udp_obj = udpSendRecieve.UDPNetwork()
    timeout = 2  # 100 ms by default unless changed by constructor
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
        # self.unique_request_id.append( binascii.hexlify(
        #     socket.inet_aton(socket.gethostbyname(socket.gethostname()))
        # ).upper()
        # )# IP 4 bytes
        # self.unique_request_id.append(struct.unpack("xH", struct.pack("i", int(self.local_port))))  # Port 2 bytes
        #  self.unique_request_id.append(struct.unpack("xH", struct.pack("i", int(time.strftime("%M")))))  # Local time 2 bytes

        ip = binascii.hexlify(
            socket.inet_aton(socket.gethostbyname(socket.gethostname()))
        ).upper()
        port = binascii.hexlify(
            struct.pack("H", int(self.local_port))
        ).upper()

        # ip = socket.inet_aton(socket.gethostbyname(socket.gethostname()))
        # port = struct.pack("H", int(self.local_port))
        local_time = binascii.hexlify(
            struct.pack("H", int(time.strftime("%M")))
        ).upper()
        # local_time = struct.pack("H", int(time.strftime("%M")))


        self.unique_request_id = ip + port + local_time

        # self.message = binascii.hexlify(
        #     # map(hex, array("B", self.message))
        #     self.message
        # )
        # print "self.message:" + self.message
        # to_send = str(self.unique_request_id) + str(self.message)
        # print "to send:" + to_send

        self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id + self.message)
        # print "sent: self.unique_request_id + self.message:"+ self.unique_request_id + self.message.encode('hex')

    def receive(self):
        resend_counter = 1
        timeout = self.timeout
        while resend_counter <= 3:
            try:
                data, addr = self.udp_obj.receive(44444, timeout)
                received_header = data[0:16]
                payload = data[16:]
                # print "data:" + data
                # print "unique_request_id:" + self.unique_request_id
                # print "received_header:" + received_header +\
                #       ", payload:" + payload +\
                #       ", length:" + str(len(received_header))

                print "Unique ID: " + str(self.unique_request_id) + " received_header: " + str(received_header) + "\n"

                if self.unique_request_id == received_header:
                    return payload
            except socket.error:
                resend_counter += 1
                timeout *= 2
                self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id + self.message)
                # print "socket.error: " + str(socket.error)
                print "Timeout: " + str(timeout) +"ms. Sending again, trail: " + str(resend_counter)

        return -1


