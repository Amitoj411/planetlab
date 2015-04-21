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
import partitioning

sleep_time = .1
numberOfMsgs = 1
timeout = 1

def add(compoenent_name):
    print "Add start", compoenent_name
    t = 0
    while t < 100000:
        t += 1

global sum__
sum__ = 0

global sum_process
sum_process = 0

global avg
avg =0
global sum_time_process_success
sum_time_process_success = 0

global max_time_process_success
max_time_process_success = -1

global min_time_process_success
min_time_process_success = 9999999

global sum_time_process_fail
sum_time_process_fail = 0

global max_time_process_fail
max_time_process_fail = -1

global min_time_process_fail
min_time_process_fail = 9999999

sum_time_process_success_list = []


def send(game_id, component):
    global sum__
    global sum_process
    global avg
    global sum_time_process_success
    global max_time_process_success
    global min_time_process_success
    global sum_time_process_fail
    global max_time_process_fail
    global min_time_process_fail

    to_node = 0
    request_key = game_id + component
    request_value = ""
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

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv, "", [""])
    N = 3
    hashedKeyModN = -1
    mode = "client"
    # wireObj = wire.Wire(int(N), hashedKeyModN, Mode.local, mode)
    settings.init(N,hashedKeyModN,mode)
    wireObj = wire.Wire(3, 0, Mode.local, "main")
    client_id = args[1]
    game_id = args[2]


    for count in range(numberOfMsgs):
        time.sleep(sleep_time)
        print "game" + str(count)
        # request_key = client_id = args[1]
        # request_value = game_id = "game1"

        dagObj = partitioning.parse_game_dag(settings.game_dag.get(game_id))
        for component in dagObj:
            if component.isMobile == 'm':
                add(component.name)
            else:  # Run component on the cloud
                send(game_id, component.name)
            last_component_name = component.connectTo_name
            last_component_isMobile = component.connectTo_isMobile

        if last_component_isMobile == 'm':
            add(last_component_name)
        else:  # Run component on the cloud
            send(game_id, last_component_name)


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