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



numberOfMsgs = 15
retrial_times = 0
sleep_time = .1
timeout = 2
number_of_nodes = 5
# observer_node = 0


# sum_put = [-1] * number_of_nodes
# sum_get = [-1] * number_of_nodes
# sum_remove = [-1] * number_of_nodes

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

    # for i in range(0, number_of_nodes - 1):
    # for i in range(0, 1):
    #     print "**************"
    #     print "**ROUND == " + str(i) + "**"
    #     print "**************"
    #
    #     # Delete everything that was put before.
    #     if i != 0:


    node_id = 0
    sum = 0
    sum_time_put_success = 0
    max_time_put_success = -1
    min_time_put_success = 9999999
    sum_time_put_fail = 0
    max_time_put_fail = -1
    min_time_put_fail = 9999999
    for seed in range(0, numberOfMsgs):
        print "seed:" + str(seed) + ", node id:" + str(node_id)
        wireObj.send_request(Command.PUT, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
                             0, timeout, retrials=retrial_times)  # send to node 0
        start = time.time()
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
        if response_code == Response.SUCCESS:
            dt = int((time.time() - start) * 1000)
            sum_time_put_success += dt
            if dt > max_time_put_success:
                max_time_put_success = dt
            if dt < min_time_put_success:
                min_time_put_success = dt
            print dt
        else:
            dt2 = int((time.time() - start) * 1000)
            sum_time_put_fail += dt2
            if dt2 > max_time_put_fail:
                max_time_put_fail = dt2
            if dt2 < min_time_put_fail:
                min_time_put_fail = dt2
            print dt2
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
    sum_put = sum

    # time.sleep(5)

    # wireObj.send_request(Command.SHUTDOWN, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
    #                      next(i), timeout, retrials=retrial_times)  # kill i+1
    # response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)

    # time.sleep(5)

    # _ = raw_input('Ready to get?>')
    node_id = 2
    sum = 0
    sum_time_get_success = 0
    max_time_get_success = -1
    min_time_get_success = 9999999
    sum_time_get_fail = 0
    max_time_get_fail = -1
    min_time_get_fail = 9999999
    for seed in range(numberOfMsgs - 1, -1, -1):  # Arbitrary 14 msgs sent
        print "seed(backward):" + str(seed) + ", node id:" + str(node_id)

        wireObj.send_request(Command.GET, str(seed), len(value_to_send), value_to_send, threading.currentThread(), 0
                             , timeout, retrials=retrial_times)  # send to node 0
        start = time.time()
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.GET)
        if response_code == Response.SUCCESS:
            dt = int((time.time() - start) * 1000)
            sum_time_get_success += dt
            if dt > max_time_get_success:
                max_time_get_success = dt
            if dt < min_time_get_success:
                min_time_get_success = dt
            print dt
        else:
            dt2 = int((time.time() - start) * 1000)
            sum_time_get_fail += dt2
            if dt2 > max_time_get_success:
                max_time_get_fail = dt2
            if dt2 < min_time_get_success:
                min_time_get_fail = dt2
            print dt2
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
    sum_get= sum


    node_id = 0
    sum = 0
    sum_time_remove_success = 0
    max_time_remove_success = -1
    min_time_remove_success = 9999999
    sum_time_remove_fail = 0
    max_time_remove_fail = -1
    min_time_remove_fail = 9999999
    for seed in range(0, numberOfMsgs):
        print "seed:" + str(seed) + ", node id:" + str(node_id)
        wireObj.send_request(Command.REMOVE, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
                             0, timeout, retrials=retrial_times)  # send to node 0
        start = time.time()
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.REMOVE)
        if response_code == Response.SUCCESS:
            dt = int((time.time() - start) * 1000)
            sum_time_remove_success += dt
            if dt > max_time_remove_success:
                max_time_remove_success = dt
            if dt < min_time_remove_success:
                min_time_remove_success = dt
            print dt
        else:
            dt2 = int((time.time() - start) * 1000)
            sum_time_remove_fail += dt2
            if dt2 > max_time_remove_success:
                max_time_remove_fail = dt2
            if dt2 < min_time_remove_success:
                min_time_remove_fail = dt2
            print dt2
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
    sum_remove=sum

    # for i in range(0, number_of_nodes - 1):
    # for i in range(0, 1):
    #     print "Round: " + str(i + 1)
    print "Total successful PUT: " + str(sum_put) + "/" + str(numberOfMsgs)
    # print "\n"
    print "sum_time_add_success: ", sum_time_put_success
    print "max_time_add_success: ", max_time_put_success
    print "min_time_add_success: ", min_time_put_success
    if sum_get != 0:
        print "AVG:: " + str(sum_time_put_success/sum_put)
    else:
        print "AVG:: " + 'zero'
    print "sum_time_add_fail: ", sum_time_put_fail
    print "max_time_add_fail: ", max_time_put_fail
    print "min_time_add_fail: ", min_time_put_fail
    if sum_put != numberOfMsgs:
        print "AVG:: " + str(sum_time_put_fail / (numberOfMsgs - sum_put))
    else:
        print "AVG:: " + "zero"

    print "\n"


    print "Total successful GET: " + str(sum_get) + "/" + str(numberOfMsgs)
    print "sum_time_get_success: ", sum_time_get_success
    print "max_time_get_success: ", max_time_get_success
    print "min_time_get_success: ", min_time_get_success
    if sum_get != 0:
        print "AVG:: " + str(sum_time_get_success/sum_get)
    else:
        print "AVG:: ", 'zero'
    print "sum_time_get_fail: ", sum_time_get_fail
    print "max_time_get_fail: ", max_time_get_fail
    print "min_time_get_fail: ", min_time_get_fail
    if sum_get != numberOfMsgs:
        print "AVG:: " + str(sum_time_get_fail/(numberOfMsgs - sum_get))
    else:
        print "AVG:: ", 'zero'
    print "\n"

    print "Total successful REMOVE: " + str(sum_remove) + "/" + str(numberOfMsgs)
    print "sum_time_remove_success: ", sum_time_remove_success
    print "max_time_remove_success: ", max_time_remove_success
    print "min_time_remove_success: ", min_time_remove_success
    if sum_remove != 0:
        print "AVG:: " + str(sum_time_remove_success/sum_remove)
    else:
        print "AVG:: ", 'Zero'

    print "sum_time_remove_fail: ", sum_time_remove_fail
    print "max_time_remove_fail: ", max_time_remove_fail
    print "min_time_remove_fail: ", min_time_remove_fail
    if sum_remove != numberOfMsgs:
        print "AVG:: " + str(sum_time_remove_fail/(numberOfMsgs - sum_remove))
    else:
        print "AVG:: ", 'Zero'

        # _ = raw_input('Continue to next round?>')