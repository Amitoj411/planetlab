__author__ = 'Owner'
import wire
import Mode
import ring
import Command
import time
from Response import print_response
import threading

if __name__ == "__main__":
    kvTable = ring.Ring()
    wireObj = wire.Wire(3, 0, Mode.local)

    value_to_send = "Any......."

    # Build 100 character msg
    for i in range(2):
        value_to_send += "1234567890"

    # seed = 0
    node_id = 0

    for seed in range(0, 15):  # Arbitrary 15 msgs sent
        print "seed:" + str(seed) + ", node id:" + str(node_id)

        wireObj.send_request(Command.PUT, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
                             0, .1)  # send to node 0
        response_code, value = wireObj.receive_reply(threading.currentThread())
        print print_response(response_code)

        node_id += 1

        if node_id == 3:
            node_id = 0
        time.sleep(1)

    _ = raw_input('Ready to get?>')
    node_id = 2
    for seed in range(14, -1, -1):  # Arbitrary 14 msgs sent
        print "seed(backward):" + str(seed) + ", node id:" + str(node_id)

        wireObj.send_request(Command.GET, str(seed), len(value_to_send), value_to_send, threading.currentThread(), 0
                             , .1)  # send to node 0
        response_code, value = wireObj.receive_reply(threading.currentThread())
        print print_response(response_code)

        node_id -= 1

        if node_id == -1:
            node_id = 2

        # time.sleep(3)
