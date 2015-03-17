__author__ = 'Owner'
import wire
import Mode
import ring
import Command
from Response import print_response
import threading
if __name__ == "__main__":
    kvTable = ring.Ring()
    wireObj = wire.Wire(3, 1, Mode.testing)

    value_to_send = "Any......."
    seed = 0
    # Build 100 character msg
    for i in range(2):
        value_to_send += "1234567890"

    node_id = 0

    while True:
        seed += 1
        print "seed:" + str(seed)

        wireObj.send_request(Command.PUT, str(seed), len(value_to_send), value_to_send,
                             threading.currentThread(), node_id)  # send to node 0
        response_code, value = wireObj.receive_reply(threading.currentThread())
        print_response(response_code)

        node_id += 1

        if node_id == 3:
            node_id = 0