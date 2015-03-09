__author__ = 'Owner'

import Colors

Main = 01
AvailabilityAndConsistency = 02
Wire = 03
RequestReplyClient = 04

debug = False


def print_(string, mode, node_id):
    if debug:
        node_id = str(node_id)
        if mode == Main:
            print "main$[node_id:" + node_id + "] " + string + Colors.Colors.ENDC
        elif mode == Wire:
            print Colors.Colors.OKGREEN + "Wire$[node_id:" + node_id + "] " + string + Colors.Colors.ENDC
        elif mode == AvailabilityAndConsistency:
            print Colors.Colors.OKBLUE + "AvailabilityAndConsistency$[node_id:" + node_id + "] " \
                   + string + Colors.Colors.ENDC
        elif mode == RequestReplyClient:
            print Colors.Colors.WARNING + "RequestReplyClient$[node_id:" + node_id + "] " + string + Colors.Colors.ENDC