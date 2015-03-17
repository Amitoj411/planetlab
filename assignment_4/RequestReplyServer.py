__author__ = 'Owner'
# To-Do do whatever we did in assignment 1
# import socket
# import time
# import binascii
# import struct
import array
import udpSendRecieve
import HashTable
import Print

class Message:
    ip = ""
    port = ""
    msg = ""

    def __init__(self, ip, port, msg):
        self.ip = ip
        self.port = port
        self.msg = msg


class RequestReplyServer:
    udp_obj = udpSendRecieve.UDPNetwork()
    timeout = .1  # 100 ms by default unless changed by constructor
    # For retransmission
    unique_request_id = array.array('b')  # last id was send. Used to match the most recent received one
    # udp_ip = ""
    # udp_port = ""
    # message = ""
    # local_port = ""
    cache = HashTable.HashTable("ServerCache")

    def __init__(self, timeout):
        # self.udp_ip = udp_ip
        # self.udp_port = udp_port
        # self.message = message
        # self.local_port = local_port
        self.timeout = timeout
        self.cache.clean()

    def send(self, udp_ip, udp_port, message):
        # Prepare the header as A1
        # print "self.unique_request_id(Server):" + self.unique_request_id

        # Add to the server cache
        msgObj = Message(udp_ip, udp_port, message)
        self.cache.put(self.unique_request_id, msgObj)

        self.udp_obj.send(udp_ip, int(udp_port), self.unique_request_id + message, "server")

    def receive(self, udp_port, handler, cur_thread, local_node_id):
        while True:
            data, addr = self.udp_obj.receive(udp_port, self.timeout, handler, cur_thread)

            # print "data:" + data + ", data length:" + str(len(data)) +\
            #       ",received_header:" + received_header +\
            #       ", length(received_header):" + str(len(received_header))

            received_header = data[0:16]
            data = data[16:]
            # Check the server cache before replying back to the client
            if self.cache.get(received_header) is None:  # msg Does not exist in the cache
                self.unique_request_id = received_header
                return received_header, data, addr
            else:  # duplicate msgs
                # send the reply again
                msgObj = self.cache.get(received_header)
                self.udp_obj.send(msgObj.ip, int(msgObj.port), received_header + msgObj.msg, "server")
                Print.print_("RequestReplyServer$ Duplicate: " + " Sending reply again, " ,
                             Print.RequestReplyClient, local_node_id, cur_thread)

                # self.udp_obj.send(self.udp_ip, self.udp_port, self.unique_request_id + self.message,
                #               "client")
                continue






