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
    timeout = 2  # 100 ms by default unless changed by constructor
    # For retransmission
    unique_request_id = array.array('b')  # last id was send. Used to match the most recent received one
    # unique_request_id = []# last id was send. Used to match the most recent received one
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
        # self.unique_request_id = bytearray(16)
        self.unique_request_id = socket.inet_aton(socket.gethostbyname(socket.gethostname())) +  \
                                 struct.pack("QHH", int(time.strftime("%M")), int(self.local_port), random.randint(0,10))
        # print  Colors.Colors.WARNING + "RequestReplyClient$ len(unique_request_id) : " + \
        #        str(len(self.unique_request_id)) + Colors.Colors.ENDC


        # ip = binascii.hexlify(
        #     socket.inet_aton(socket.gethostbyname(socket.gethostname()))
        # ).upper()
        # port = binascii.hexlify(
        #     struct.pack("H", int(self.local_port))
        # ).upper()
        # local_time = binascii.hexlify(
        #     struct.pack("H", int(time.strftime("%M")))
        # ).upper()

        # ip = socket.inet_aton(socket.gethostbyname(socket.gethostname()))
        # port = struct.pack("H", int(self.local_port))
        # local_time = struct.pack("Q", int(time.strftime("%M")))
        # rand = struct.pack("H", random.randint(0,10))

        # self.unique_request_id = ip + port + local_time
        # self.unique_request_id.append(ip)
        # self.unique_request_id.append(port)
        # self.unique_request_id.append(local_time)
        # self.unique_request_id.append(random)

        # self.message = binascii.hexlify(
        #     # map(hex, array("B", self.message))
        #     self.message
        # )
        # print "self.message:" + self.message
        # to_send = str(self.unique_request_id) + str(self.message)
        # print "to send:" + to_send

        # self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id+ self.message)
        self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id + self.message)


    def receive(self, port_number, local_node_id):
        resend_counter = 1
        timeout = self.timeout
        while resend_counter <= 3:
            try:
                data, addr = self.udp_obj.receive(port_number, timeout)
                received_header = data[0:16]
                payload = data[16:]
                # print "data:" + data
                # print "unique_request_id:" + self.unique_request_id
                # print "received_header:" + received_header +\
                #       ", payload:" + payload +\
                #       ", length:" + str(len(received_header))

                # print Colors.Colors.WARNING \
                #     + "RequestReplyClient$: " \
                #     + ", Unique ID: " + str(self.unique_request_id) \
                #     + ", received_header: " + str(received_header) \
                #     + Colors.Colors.ENDC

                if self.unique_request_id == received_header:
                    return payload
            except socket.error:
                resend_counter += 1
                timeout *= 2
                Print.print_("RequestReplyClient$ Timeout: " + str(timeout) + \
                      "s. Sending again, trail: " + str(resend_counter), Print.RequestReplyClient, local_node_id)
                self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id + self.message)
                # print "socket.error: " + str(socket.error)


        return -1


