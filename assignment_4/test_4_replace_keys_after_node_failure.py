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

if __name__ == "__main__":
    kvTable = ring.Ring()
    wireObj = wire.Wire(3, 0, Mode.local)

    numberOfMsgs = 100
    retrial_times = 0
    sleep_time = 0

    node_id = 0
    sum = 0
    timeout = 2

    wireObj.send_request(Command.PUT, str('app'), len("red"), "red", threading.currentThread(),
                         1, timeout, retrials=retrial_times)  # send to node 0
    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
    print print_response(response_code) + "\n"

    wireObj.send_request(Command.SHUTDOWN, str('app'), len(''), '', threading.currentThread(),
                         0, timeout, retrials=retrial_times)  # send to node 0
    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
    print print_response(response_code) + "\n"

    wireObj.send_request(Command.PUT, str('app'), len('r'), 'r', threading.currentThread(),
                         1, timeout, retrials=retrial_times)  # send to node 0
    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
    print print_response(response_code) + "\n"

    wireObj.send_request(Command.GET, str('app'), len(''), '', threading.currentThread(),
                         1, timeout, retrials=retrial_times)  # send to node 0
    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
    print print_response(response_code) + "\n"

    # wireObj.send_request(Command.REMOVE, str('app'), len(value_to_send), value_to_send, threading.currentThread(),
    #                      1, timeout, retrials=retrial_times)  # send to node 0
    # response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
    # print print_response(response_code) + "\n"