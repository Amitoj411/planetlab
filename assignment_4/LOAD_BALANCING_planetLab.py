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

    value_to_send = "Any......."


    for i in range(2):
        value_to_send += "1234567890"

    numberOfMsgs = 18
    retrial_times = 0
    sleep_time = 0
    timeout = 1

    node_id = 0
    sum = 0
    for seed in range(0, numberOfMsgs):
        print "seed:" + str(seed) + ", node id:" + str(node_id)

        wireObj.send_request(Command.PUT, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
                             0, timeout, retrials=retrial_times)  # send to node 0
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
        print print_response(response_code) + "\n"

        node_id += 1

        if node_id == 3:
            node_id = 0

        if response_code == Response.SUCCESS:
            sum += 1
        else:
            print "************************************************************"
            print "************************************************************"
        time.sleep(sleep_time)
    print "Total successful PUT: " + str(sum) + "/" + str(numberOfMsgs)

    _ = raw_input('Ready to get?>')
    node_id = 2
    sum_get = 0
    for seed in range(numberOfMsgs - 1, -1, -1):  # Arbitrary 14 msgs sent
        print "seed(backward):" + str(seed) + ", node id:" + str(node_id)

        wireObj.send_request(Command.GET, str(seed), len(value_to_send), value_to_send, threading.currentThread(), 0
                             , timeout, retrials=retrial_times)  # send to node 0
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.GET)
        print print_response(response_code) + "\n"

        node_id -= 1

        if node_id == -1:
            node_id = 2

        if response_code == Response.SUCCESS:
            sum_get += 1
        else:
            print "************************************************************"
            print "************************************************************"
        time.sleep(sleep_time)

    print "Total successful PUT: " + str(sum) + "/" + str(numberOfMsgs)
    print "Total successful GET: " + str(sum_get) + "/" + str(numberOfMsgs)


    _ = raw_input('Ready to REMOVE?>')
    sum_remove = 0
    count = 0
    for seed in range(numberOfMsgs - 1, -1, -1):
        print "count:" + str(count)
        count += 1
        print "seed(backward):" + str(seed) + ", node id:" + str(node_id)

        wireObj.send_request(Command.REMOVE, str(seed), len(value_to_send), value_to_send, threading.currentThread(), 0
                             , timeout, retrials=retrial_times)  # send to node 0
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.GET)
        print print_response(response_code) + "\n"

        node_id -= 1

        if node_id == -1:
            node_id = 2

        if response_code == Response.SUCCESS:
            sum_remove += 1
        time.sleep(sleep_time)

    print "Total successful PUT: " + str(sum) + "/" + str(numberOfMsgs)
    print "Total successful GET: " + str(sum_get) + "/" + str(numberOfMsgs)
    print "Total successful REMOVE: " + str(sum_remove) + "/" + str(numberOfMsgs)

    sum_get_after = 0
    # _ = raw_input('Ready to GET after REMOVE?>')
    for seed in range(numberOfMsgs - 1, -1, -1):  # Arbitrary 14 msgs sent
        print "seed(backward):" + str(seed) + ", node id:" + str(node_id)

        wireObj.send_request(Command.GET, str(seed), len(value_to_send), value_to_send, threading.currentThread(), 0
                             , timeout, retrials=retrial_times)  # send to node 0
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.GET)
        print print_response(response_code) + "\n"

        node_id -= 1

        if node_id == -1:
            node_id = 2

        if response_code == Response.NONEXISTENTKEY:
            sum_get_after += 1
        time.sleep(sleep_time)

    print "Total successful PUT: " + str(sum) + "/" + str(numberOfMsgs)
    print "Total successful GET: " + str(sum_get) + "/" + str(numberOfMsgs)
    print "Total successful REMOVE: " + str(sum_remove) + "/" + str(numberOfMsgs)
    print "Total NONEXISTENTKEY GET: " + str(sum_get_after) + "/" + str(numberOfMsgs)
