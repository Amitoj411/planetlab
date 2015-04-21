__author__ = 'Owner'
# import sys
# sys.path.append("../")
import wire
import Mode
import ring
import Command
import time
from Response import print_response
import threading
import Response
import struct
import RequestReplyClient
import NodeList
import socket
import random
import udpSendRecieve
if __name__ == "__main__":
    kvTable = ring.Ring()
    wireObj = wire.Wire(3, 0, Mode.local)

    wireObj.send_request(Command.PUT, str('app'), len('red'), 'red', threading.currentThread(),
                         0, .1, retrials=0)  # send to node 0
    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)

    msg = struct.pack("<B32s", Command.GET, "app")
    ip_port = NodeList.look_up_node_id(hash("app") % 3, "local")
    # RequestReplyClient_obj = RequestReplyClient.RequestReplyClient(ip_port.split(':')[0],
    #                                                                         ip_port.split(':')[1],
    #                                                                         msg,
    #                                                                         "50000",
    #                                                                         .1,
    #                                                                         0)
    unique_request_id = socket.inet_aton(socket.gethostbyname(socket.gethostname())) + \
                         struct.pack("QHH",
                         int(time.time() * 10000 % 10000),
                         int(ip_port.split(':')[1]),
                         random.randint(0, 100))


    # wireObj.send_request(Command.GET, str('app'), len('red'), 'red', threading.currentThread(),
    #                      0, .1, retrials=0)  # send to node 0
    # response_code, reply = wireObj.receive_reply(threading.currentThread(), Command.PUT)
    # print reply
    #
    #
    #
    # wireObj.send_request(Command.GET, str('app'), len('red'), 'red', threading.currentThread(),
    #                      0, .1, retrials=0)  # send to node 0
    # response_code, reply = wireObj.receive_reply(threading.currentThread(), Command.PUT)
    # print reply







    udp_obj = udpSendRecieve.UDPNetwork()
    udp_obj.send_request(ip_port.split(':')[0], ip_port.split(':')[1], unique_request_id + msg, "client")
    reply = udp_obj.wait_reply(1)
    print reply
    #

    time.sleep(.1)
    udp_obj2 = udpSendRecieve.UDPNetwork()
    udp_obj2.send_request(ip_port.split(':')[0], ip_port.split(':')[1], unique_request_id + msg, "client")
    reply = udp_obj2.wait_reply(1)
    print reply

    time.sleep(10) # Most likely it gonna work
    udp_obj2 = udpSendRecieve.UDPNetwork()
    udp_obj2.send_request(ip_port.split(':')[0], ip_port.split(':')[1], unique_request_id + msg, "client")
    reply = udp_obj2.wait_reply(1)
    print reply


