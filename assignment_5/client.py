__author__ = 'Owner'
import wire
import getopt
import sys
import xmlrpclib
import time
import settings
import Mode
import NodeList
import AvailabilityAndConsistency
import Command
import Response
import threading
import math


sleep_time = .1
numberOfMsgs = 100
timeout = 1

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv, "", [""])
    N = 3
    hashedKeyModN = -1
    mode = "client"
    # wireObj = wire.Wire(int(N), hashedKeyModN, Mode.local, mode)
    settings.init(N,hashedKeyModN,mode)
    wireObj = wire.Wire(3, 0, Mode.local, "main")

    sum__ = 0
    sum_time_process_success = 0
    max_time_process_success = -1
    min_time_process_success = 9999999
    sum_time_process_fail = 0
    max_time_process_fail = -1
    min_time_process_fail = 9999999
    sum_time_process_success_list = []
    for count in range(numberOfMsgs):
        time.sleep(sleep_time)
        print "game" + str(count)
        request_key = client_id = args[1]
        request_value = game_id = "simulation" + str(count)

        to_node = 0
        wireObj.send_request(Command.EXECUTE, request_key, len(request_value), request_value, threading.currentThread(), to_node, timeout, 0)
        start = time.time()
        # TODO: Search function; assume node 0 is always alive for now. Later search function
        response_code, response_value = wireObj.receive_reply(threading.currentThread(), Command.EXECUTE)
        # dt = int((time.time() - start) * 1000)


        if response_code == Response.SUCCESS:
            dt = int((time.time() - start) * 1000)
            sum_time_process_success += dt
            sum_time_process_success_list.append(dt)
            if dt > max_time_process_success:
                max_time_process_success = dt
            if dt < min_time_process_success:
                min_time_process_success = dt
            print dt
        else:
            dt2 = int((time.time() - start) * 1000)
            sum_time_process_fail += dt2
            if dt2 > max_time_process_fail:
                max_time_process_fail = dt2
            if dt2 < min_time_process_fail:
                min_time_process_fail = dt2
            print dt2

        if response_code == Response.SUCCESS:
            sum__ += 1
        else:
            print "************************************************************"
            print "************************************************************"

        print "Total successful Process: " + str(sum__) + "/" + str(numberOfMsgs)
    sum_process = sum__

    print "Total successful Process: " + str(sum_process) + "/" + str(numberOfMsgs)
    print "Percentage of correctly served requests", sum_process / numberOfMsgs * 100.0, '%100'
    print "sum_time_process_success: ", sum_time_process_success, 'ms'
    print "max_time_process_success: ", max_time_process_success, 'ms'
    print "min_time_process_success: ", min_time_process_success, 'ms'
    if sum_process != 0:
        avg = sum_time_process_success / sum_process * 1.0
        print "AVG:: " + str(avg), 'ms'
        sum_ = 0
        for x in sum_time_process_success_list:
            sum_ += math.pow(x - avg, 2)
        print "Std. Var. :: " + str(math.sqrt(sum_ / sum_process)), 'ms'
    else:
        print "AVG:: " + 'zero'
    print "Goodput::", avg, 'ms'
    print "\n"
    print "sum_time_process_fail: ", sum_time_process_fail
    print "max_time_process_fail: ", max_time_process_fail
    print "min_time_process_fail: ", min_time_process_fail
    if sum_process != numberOfMsgs:
        print "AVG:: " + str(sum_time_process_fail / (numberOfMsgs - sum_process))
    else:
        print "AVG:: " + "zero"

    print "\n"
    print "\n"

        # if response_code == Response.SUCCESS:
        #     print "RTT:", dt, "Computing Server Node_id", response_value
        # else:
        #     print Response.print_response(response_code)
        #     print "RTT:", dt, "Computing Server Node_id", response_value

        # RECEIVE COMPUTING SERVER ID
        # SEND RPC client REQUEST
    # print client_id + game_id , "hash(client_id + game_id) % int(N)" , hash(client_id + game_id)% int(N)
    # computing_server_node_id = hash(client_id + game_id) % int(N)
    # ip_port_ = NodeList.look_up_node_id(computing_server_node_id, mode)
    # computing_server_ip = ip_port_.split(':')[0]
    # computing_server_port = int(ip_port_.split(':')[1]) + 2000

    # succesor_1 = AvailabilityAndConsistency.successor(computing_server_node_id)
    # succesor_2 = AvailabilityAndConsistency.successor(succesor_1)
    # list_of_nodes = response_value.split(':')
    # for x in list_of_nodes:
    #     ip_port_ = NodeList.look_up_node_id(x, mode)
    #     computing_server_ip = str(ip_port_).split(':')[0]
    #     computing_server_port = str(ip_port_).split(':')[1]
    #     computing_server_ip = str(response_value).split(':')[0]
    #     computing_server_port = str(response_value).split(':')[1]
    # Also send to the successors
    # print computing_server_port
    # proxy = xmlrpclib.ServerProxy("http://" + computing_server_ip + ":" +
    #                               str(computing_server_port) + "/")
    # multicall = xmlrpclib.MultiCall(proxy)
    #
    #
    # multicall.add(7, 3)
    # # multicall.subtract(7, 3)
    # # multicall.multiply(7, 3)
    # # multicall.divide(7, 3)
    # start = time.time()
    # result = multicall()
    # dt = int((time.time() - start) * 1000)
    # print dt
    #
    # print "7+3=%d, 7-3=%d, 7*3=%d, 7/3=%d" % tuple(result)
