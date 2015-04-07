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



numberOfMsgs = 100
retrial_times = 0
sleep_time = .05
timeout = 2
number_of_nodes = 5
# observer_node = 0


sum_put = [-1] * number_of_nodes
sum_get = [-1] * number_of_nodes
sum_remove = [-1] * number_of_nodes

def next(cursor):
    if cursor == int(number_of_nodes) - 1:
        return 0
    else:
        return cursor + 1

if __name__ == "__main__":
    kvTable = ring.Ring()
    wireObj = wire.Wire(3, 0, Mode.local, "main")

    value_to_send = "Any......."

    for i in range(2):
        value_to_send += "1234567890"

    for i in range(0, number_of_nodes - 1):
    # for i in range(0, 1):
        print "**************"
        print "**ROUND == " + str(i) + "**"
        print "**************"

        # Delete everything that was put before.
        if i != 0:
            node_id = 0
            sum = 0
            for seed in range(0, numberOfMsgs):
                print "seed:" + str(seed) + ", node id:" + str(node_id)
                wireObj.send_request(Command.REMOVE, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
                                     0, timeout, retrials=retrial_times)  # send to node 0
                response_code, value = wireObj.receive_reply(threading.currentThread(), Command.REMOVE)
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
            sum_remove[i]=sum
        else:
            sum_remove[i]=0

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
        sum_put[i] = sum

        # time.sleep(5)

        wireObj.send_request(Command.SHUTDOWN, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
                             next(i), timeout, retrials=retrial_times)  # kill i+1
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)

        # time.sleep(5)

        # _ = raw_input('Ready to get?>')
        node_id = 2
        sum = 0
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
                sum += 1
            else:
                print "************************************************************"
                print "************************************************************"
            time.sleep(sleep_time)
        sum_get[i] = sum

    for i in range(0, number_of_nodes - 1):
    # for i in range(0, 1):
        print "Round: " + str(i+1)
        print "Total successful REMOVE: " + str(sum_remove[i]) + "/" + str(numberOfMsgs)
        print "Total successful PUT: " + str(sum_put[i]) + "/" + str(numberOfMsgs)
        print "Total successful GET: " + str(sum_get[i]) + "/" + str(numberOfMsgs)
        print "\n"


        # _ = raw_input('Continue to next round?>')