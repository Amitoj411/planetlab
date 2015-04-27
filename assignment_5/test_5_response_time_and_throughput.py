__author__ = 'Owner'
# import sys
# sys.path.append("../")
import wire
import Mode
import Command
import time
from Response import print_response
import threading
import Response
import math
import random



numberOfMsgs = 20
retrial_times = 0
sleep_time = .1
timeout = 1
number_of_nodes = 50
variant = "same_node"  # Node zero
# variant = "different_nodes"
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
    sum_time_put_success_list = []
    for seed in range(0, numberOfMsgs):
        print "seed:" + str(seed) + ", node id:" + str(node_id)
        if variant == "same_node":
            wireObj.send_request(Command.PUT, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
                             0, timeout, retrials=retrial_times)  # send to node 0
            start = time.time()
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
        else:
            random_node = random.randint(0, int(number_of_nodes) - 1)
            wireObj.send_request(Command.PUT, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
                             random_node, timeout, retrials=retrial_times)  # send to node 0
            start = time.time()
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)

        if response_code == Response.SUCCESS:
            dt = int((time.time() - start) * 1000)
            sum_time_put_success += dt
            sum_time_put_success_list.append(dt)
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

    _ = raw_input('Ready to get?>')
    node_id = 2
    sum = 0
    sum_time_get_success = 0
    max_time_get_success = -1
    min_time_get_success = 9999999
    sum_time_get_fail = 0
    max_time_get_fail = -1
    min_time_get_fail = 9999999
    sum_time_get_success_list = []
    for seed in range(numberOfMsgs - 1, -1, -1):  # Arbitrary 14 msgs sent
        print "seed(backward):" + str(seed) + ", node id:" + str(node_id)

        if variant == "same_node":
            wireObj.send_request(Command.GET, str(seed), len(value_to_send), value_to_send, threading.currentThread(), 0
                                 , timeout, retrials=retrial_times)  # send to node 0
            start = time.time()
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.GET)
        else:
            random_node = random.randint(0, int(number_of_nodes) - 1)
            wireObj.send_request(Command.GET, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
                             random_node, timeout, retrials=retrial_times)  # send to node 0
            start = time.time()
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
        if response_code == Response.SUCCESS:
            dt = int((time.time() - start) * 1000)
            sum_time_get_success_list.append(dt)
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

    _ = raw_input('Ready to get?>')


    node_id = 0
    sum = 0
    sum_time_remove_success = 0
    max_time_remove_success = -1
    min_time_remove_success = 9999999
    sum_time_remove_fail = 0
    max_time_remove_fail = -1
    min_time_remove_fail = 9999999
    sum_time_remove_success_list = []
    for seed in range(0, numberOfMsgs):
        print "seed:" + str(seed) + ", node id:" + str(node_id)
        if variant == "same_node":
            wireObj.send_request(Command.REMOVE, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
                                 0, timeout, retrials=retrial_times)  # send to node 0
            start = time.time()
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.REMOVE)
        else:
            random_node = random.randint(0, int(number_of_nodes) - 1)
            wireObj.send_request(Command.REMOVE, str(seed), len(value_to_send), value_to_send, threading.currentThread(),
                             random_node, timeout, retrials=retrial_times)  # send to node 0
            start = time.time()
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
        if response_code == Response.SUCCESS:
            dt = int((time.time() - start) * 1000)
            sum_time_remove_success_list.append(dt)
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
    sum_remove = sum


    print "Total successful PUT: " + str(sum_put) + "/" + str(numberOfMsgs)
    print "Percentage of correctly served requests", sum_put/numberOfMsgs * 100.0, '%100'
    print "sum_time_add_success: ", sum_time_put_success, 'ms'
    print "max_time_add_success: ", max_time_put_success, 'ms'
    print "min_time_add_success: ", min_time_put_success, 'ms'
    if sum_put != 0:
        avg = sum_time_put_success / sum_put * 1.0
        print "AVG:: " + str(avg), 'ms'
        sum_ = 0
        for x in sum_time_put_success_list:
            sum_ += math.pow(x - avg, 2)
        print "Std. Var. :: " + str(math.sqrt(sum_/sum_get)), 'ms'
    else:
        print "AVG:: " + 'zero'
    print "Good put::", avg, 'ms'
    print "\n"
    print "sum_time_add_fail: ", sum_time_put_fail
    print "max_time_add_fail: ", max_time_put_fail
    print "min_time_add_fail: ", min_time_put_fail
    if sum_put != numberOfMsgs:
        print "AVG:: " + str(sum_time_put_fail / (numberOfMsgs - sum_put))
    else:
        print "AVG:: " + "zero"

    print "\n"
    print "\n"


    print "Total successful GET: " + str(sum_get) + "/" + str(numberOfMsgs)
    print "Percentage of correctly served requests", sum_get / numberOfMsgs * 100.0, '%100'
    print "sum_time_get_success: ", sum_time_get_success, 'ms'
    print "max_time_get_success: ", max_time_get_success, 'ms'
    print "min_time_get_success: ", min_time_get_success, 'ms'
    if sum_get != 0:
        avg = sum_time_get_success / sum_put * 1.0
        print "AVG:: " + str(avg), 'ms'
        sum_ = 0
        for x in sum_time_get_success_list:
            sum_ += math.pow(x - avg, 2)
        print "Std. Var. :: " + str(math.sqrt(sum_/sum_get)), 'ms'
    else:
        print "AVG:: ", 'zero'
    print "Good put::", avg, 'ms'
    print "\n"
    print "sum_time_get_fail: ", sum_time_get_fail
    print "max_time_get_fail: ", max_time_get_fail
    print "min_time_get_fail: ", min_time_get_fail
    if sum_get != numberOfMsgs:
        print "AVG:: " + str(sum_time_get_fail/(numberOfMsgs - sum_get))
    else:
        print "AVG:: ", 'zero'
    print "\n"
    print "\n"


    print "Total successful REMOVE: " + str(sum_remove) + "/" + str(numberOfMsgs)
    print "Percentage of correctly served requests", sum_remove / numberOfMsgs * 100.0, '%100'
    print "sum_time_remove_success: ", sum_time_remove_success, 'ms'
    print "max_time_remove_success: ", max_time_remove_success, 'ms'
    print "min_time_remove_success: ", min_time_remove_success, 'ms'
    if sum_remove != 0:
        avg = sum_time_remove_success / sum_remove * 1.0
        print "AVG:: " + str(avg), 'ms'
        sum_ = 0
        for x in sum_time_remove_success_list:
            sum_ += math.pow(x - avg, 2)
        print "Std. Var. :: " + str(math.sqrt(sum_/sum_remove)), 'ms'
    else:
        print "AVG:: ", 'Zero'
    print "Good put::", avg, 'ms'
    print "\n"
    print "sum_time_remove_fail: ", sum_time_remove_fail
    print "max_time_remove_fail: ", max_time_remove_fail
    print "min_time_remove_fail: ", min_time_remove_fail
    if sum_remove != numberOfMsgs:
        print "AVG:: " + str(sum_time_remove_fail/(numberOfMsgs - sum_remove))
    else:
        print "AVG:: ", 'Zero'



    # _ = raw_input('Continue to next round?>')