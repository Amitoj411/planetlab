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
    x = 1
    # Build 100 character msg
    for i in range(10):
        value_to_send += "1234567890"

    while True:
        print x
        key = x
        x += 1
        wireObj.send_request(Command.PUT, str(key), len(value_to_send), value_to_send
                             , threading.currentThread(), 0)  # send to node 0
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
        print_response(response_code)
