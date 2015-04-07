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
import Command
import threading


class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop(len(self.items) - 1)

    def top(self):
        return self.items[len(self.items) - 1]

    def size(self):
        return len(self.items)


class Message:
    ip = ""
    port = ""
    msg = ""
    command = ""  # For logging purposes
    key = ""  # For logging purposes

    def __init__(self, ip, port, msg, command, key):
        self.ip = ip
        self.port = port
        self.msg = msg
        self.command = command
        self.key = key


class RequestReplyServer:

    timeout = .1  # 100 ms by default unless changed by constructor

    # unique_request_id = array.array('b')  # last id was send. Used to match the most recent received one


    ALIVE_PUSH_DEBUG = False
    # id = ""


    def __init__(self, timeout, id_):
        # self.udp_ip = udp_ip
        # self.udp_port = udp_port
        # self.message = message
        # self.local_port = local_port
        self.udp_obj = udpSendRecieve.UDPNetwork()
        self.timeout = timeout
        self.id = id_
        self.cache = HashTable.HashTable("ServerCache")
        self.cache.clean()
        self.stack = Stack()

    def send(self, udp_ip, udp_port, message, command, key, local_node_id):
        # Add to the server cache
        msgObj = Message(udp_ip, udp_port, message, command, key)  # Command and key just for logging
        # self.cache.put(str(self.unique_request_id), msgObj)
        # self.udp_obj.send(udp_ip, int(udp_port), self.unique_request_id + message, "server")

        top = self.stack.pop()
        self.cache.put(top, msgObj)
        self.udp_obj.send(udp_ip, int(udp_port), top + message, "server")
        # Print.print_("sent msg with this header" + top + ", stack: " + '[%s]' % ', '.join(map(str, self.stack.items)), Print.RequestReplyServer, local_node_id, threading.currentThread())


    def receive(self, udp_port, handler, cur_thread, local_node_id, command="", key=""):
        while True:
            data, addr = self.udp_obj.receive(udp_port, self.timeout, cur_thread, handler)
            received_header = data[0:16]
            data = data[16:]
            # Check the server cache before replying back to the client
            cond = self.cache.get(str(received_header))
            if cond is None:  # msg Does not exist in the cache
                self.stack.push(received_header)
                # self.unique_request_id = received_header

                # Print.print_("received msg with this header" + str(self.stack.top()) + ", stack: " + '[%s]' % ', '.join(map(str, self.stack.items)), Print.RequestReplyServer, local_node_id, cur_thread)
                return received_header, data, addr
            else:  # duplicate msgs
                # send the reply again
                # print "Duplicate MODE"
                msgObj = cond
                self.udp_obj.send(msgObj.ip, int(msgObj.port), received_header + msgObj.msg, "server")
                # if self.ALIVE_PUSH_DEBUG or (command != Command.ALIVE and command != Command.PUSH):
                Print.print_("RequestReplyServer$ Duplicate: " + " Sending reply again, "
                             + "Reply for command: " + Command.print_command(msgObj.command)
                             + " key: " + msgObj.key + ",Mode: " + str(self.id)
                             , Print.RequestReplyServer, local_node_id, cur_thread)

                # continue