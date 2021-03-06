__author__ = 'Owner'

import Colors
import time

Main = 01
AvailabilityAndConsistency = 02
Wire = 03
RequestReplyClient = 04
Cleaning_keys = 05
RequestReplyServer = 06
HEARTBEAT = 07
debug = True


def print_(string, mode, node_id, cur_thread="_"):
    if debug:
        node_id = str(node_id)
        if cur_thread == "_":
            thread = "_"
        else:
            thread = cur_thread.getName()

        if mode == Main:
            print thread + "$main$[node_id:" + node_id + "] " + "[" + str(time.time()) + "]" + string + Colors.Colors.ENDC
        elif mode == Wire:
            print Colors.Colors.OKGREEN + thread + "$Wire$[node_id:" + node_id + "] " + "[" + str(time.time()) + "]" + string + Colors.Colors.ENDC
        elif mode == AvailabilityAndConsistency:
            print Colors.Colors.OKBLUE + thread + "$AvailabilityAndConsistency$[node_id:" + node_id + "] " \
                   + "[" + str(time.time()) + "]" + string + Colors.Colors.ENDC
        elif mode == RequestReplyClient:
            print Colors.Colors.WARNING + thread + "$RequestReplyClient$[node_id:" + node_id + "] " + \
                  "[" + str(time.time()) + "]" + string + Colors.Colors.ENDC
        elif mode == RequestReplyServer:
            print Colors.Colors.WARNING + thread + "$RequestReplyServer$[node_id:" + node_id + "] " + \
                  "[" + str(time.time()) + "]" + string + Colors.Colors.ENDC
        elif mode == Cleaning_keys:
            print Colors.Colors.FAIL + thread + "$main$[node_id:" + node_id + "] " + "[" + str(time.time()) + "]" + string + Colors.Colors.ENDC
        elif mode == HEARTBEAT:
            print Colors.Colors.BOLD + thread + "$main$[node_id:" + node_id + "] " + "[" + str(time.time()) + "]" + string + Colors.Colors.ENDC