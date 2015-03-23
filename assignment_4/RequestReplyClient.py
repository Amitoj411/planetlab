__author__ = 'Owner'
# To-Do do whatever we did in assignment 1
import socket
import time
# import binascii
import struct
import udpSendRecieve
import array
import Colors
import random
import Print


class RequestReplyClient:
    udp_obj = udpSendRecieve.UDPNetwork()
    timeout = .1  # 100 ms by default unless changed by constructor
    # For retransmission
    unique_request_id = array.array('b')  # last id was send. Used to match the most recent received one
    # unique_request_id = []# last id was send. Used to match the most recent received one
    udp_ip = ""
    udp_port = ""
    message = ""
    local_port = ""
    retrials = 2

    def __init__(self, udp_ip, udp_port, message, local_port, timeout, retrials):
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.message = message
        self.local_port = local_port
        self.timeout = timeout
        self.retrials = retrials

    def send(self):
        # Prepare the header as A1
        # self.unique_request_id = bytearray(16)
        self.unique_request_id = socket.inet_aton(socket.gethostbyname(socket.gethostname())) + \
                                 struct.pack("QHH",
                                 # int(time.strftime("%M")),
                                 int(time.time() * 10000 % 10000),
                                 int(self.local_port),
                                 random.randint(0, 100))

        self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id + self.message, "client")

    def receive_reply(self, local_node_id, cur_thread):
        resend_counter = 1
        timeout = self.timeout
        while resend_counter <= self.retrials + 1:
            try:
                data, addr = self.udp_obj.reply(timeout)
                received_header = data[0:16]
                payload = data[16:]
                # print "payload: " + payload
                if self.unique_request_id == received_header:
                    return payload
                # else:
                    # TODO check the bad cases
                    # print "bad 16:" + received_header
            except socket.error:
                if self.retrials != 0:
                    resend_counter += 1
                    timeout *= 2
                    # Print.print_("RequestReplyClient$ Timeout: " + str(timeout) + \
                    #       "s. Sending again, trail: " + str(resend_counter-1),
                    #              Print.RequestReplyClient, local_node_id, cur_thread)
                    self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id + self.message,
                                  "client")
                else:
                    break
        return -1




