__author__ = 'Owner'

import settings
import Command
import Response
import Print
import wire
import MembershipProtocol
import AvailabilityAndConsistency
import threading
import time
import main

# def init():
#     global settings.wireObj_replicate
#     settings.wireObj_replicate = wire.Wire(int(settings.N), settings.hashedKeyModN, settings.mode, "replicate", settings.successor_list)


def replicate(command, key, value=""):
    # global successor_list
    Print.print_("replicating: ", Print.Main, settings.hashedKeyModN, threading.currentThread())
    if command == Command.PUT:
        # put on the next three nodes
        AvailabilityAndConsistency.update_successor_list()
        unique_set = set(settings.successor_list)

        for x in unique_set:
            if x != int(settings.hashedKeyModN) and x != -1:
                settings.wireObj_replicate.send_request(Command.REPLICATE_PUT, key, len(value), value, threading.currentThread(), x)
                response_code, value_ = settings.wireObj_replicate.receive_reply(threading.currentThread(), Command.REPLICATE_PUT)
                # if response_code != Response.SUCCESS  # Check aliveness and dix the successor list
                # There is no nodes in the network"
            # else:
                # print "No successors found. No replicaiton. " + str(x)
                # No replications then!
    elif command == Command.REMOVE:
        # remove on the next three nodes
        AvailabilityAndConsistency.update_successor_list()
        for x in settings.successor_list:
            if x != int(settings.hashedKeyModN) and x != -1:
                settings.wireObj_replicate.send_request(Command.REPLICATE_REMOVE, key, len(value), value, threading.currentThread(), x)
                response_code, value = settings.wireObj_replicate.receive_reply(threading.currentThread(), Command.REPLICATE_REMOVE)
                # if response_code != Response.SUCCESS  # Check aliveness and dix the successor list
                # There is no nodes in the network"
            else:
                Print.print_("No successors found. No replicaiton", Print.Main, settings.hashedKeyModN, threading.currentThread())
                # No replications then!


def receive_request_replicate_only(handler=""):
    while True:
        cur_thread = threading.currentThread()
        command, key, value_length, value, sender_addr, sixteen_byte_header = settings.wireObj_replicate.receive_request(settings.hashedKeyModN, cur_thread, handler)

        if command == Command.REPLICATE_PUT:
            response = main.try_to_put(key, value)
            settings.wireObj_replicate.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REPLICATE_PUT, sixteen_byte_header)

        elif command == Command.REPLICATE_REMOVE:
            response = main.try_to_remove(key)
            settings.wireObj_replicate.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REPLICATE_REMOVE, sixteen_byte_header)


        



def clean_up_replicated_keys():
    while True:
        time.sleep(10)
        for key, value in settings.kvTable.hashTable.items():
            node_id = hash(key) % int(settings.N)
            if node_id != int(settings.hashedKeyModN):
                s = AvailabilityAndConsistency.get_direct_successor(key)

                if int(settings.hashedKeyModN) not in s \
                    and settings.aliveNessTable.get(str(s[0])) >= 0\
                    and settings.aliveNessTable.get(str(s[1])) >= 0:
                    # and settings.aliveNessTable.get(str(s[2])) >= 0:
                    Print.print_("clean_up_replicated_keys" + ",Key: " + key + ",Node: " + str(node_id) + ", get_direct_successor: " + str(s), Print.Cleaning_keys, settings.hashedKeyModN, threading.currentThread())
                    settings.kvTable.remove(key)
                    Print.print_("Key is deleted. All successors are up and alive", Print.Cleaning_keys, settings.hashedKeyModN, threading.currentThread())
                # else:
                #     print "Key is not deleted"