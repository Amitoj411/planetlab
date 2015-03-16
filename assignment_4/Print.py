__author__ = 'Owner'

import Colors

Main = 01
AvailabilityAndConsistency = 02
Wire = 03
RequestReplyClient = 04

debug = True


def print_(string, mode, node_id, cur_thread="_"):
    if debug:
        node_id = str(node_id)
        if cur_thread == "_":
            thread = "_"
        else:
            thread = cur_thread.getName()

        if mode == Main:
            print thread + "$main$[node_id:" + node_id + "] " + string + Colors.Colors.ENDC
        elif mode == Wire:
            print Colors.Colors.OKGREEN + thread + "$Wire$[node_id:" + node_id + "] " + string + Colors.Colors.ENDC
        elif mode == AvailabilityAndConsistency:
            print Colors.Colors.OKBLUE + thread + "$AvailabilityAndConsistency$[node_id:" + node_id + "] " \
                   + string + Colors.Colors.ENDC
        elif mode == RequestReplyClient:
            print Colors.Colors.WARNING + thread + "$RequestReplyClient$[node_id:" + node_id + "] " + string + Colors.Colors.ENDC