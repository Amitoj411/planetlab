from __future__ import with_statement # 2.5 only
__author__ = 'Owner'
import wire
import getopt
import sys
import threading
import Command
import os
import AvailabilityAndConsistency
import time
import Mode
import Print
import Exceptions
import SocketServer
import NodeList
import HashTable
import math
import random
import Response

def prev(key):
    if key == 0:
        return int(N) - 1
    else:
        return key - 1

def next(cursor):
    if cursor == int(N) - 1:
        return 0
    else:
        return cursor + 1


def search(key, retrieve_mode="ping"):
    local_node = int(hashedKeyModN)
    cursor = hash(key) % int(N)

    # Key Locally Stored - Preliminary check to see if you are the node the key should be stored on.
    if cursor == local_node:
        Print.print_("Local Key" + "\n",
                     Print.AvailabilityAndConsistency, local_node)
        return local_node

    # cursor = hashedNodeID           # Cursor goes through the range of nodes in our system
    while True:
        if cursor == local_node:
            print "stop: " + str(cursor)
            return local_node

        # point cursor to the prev node
        cursor = prev(cursor)

        # After 3 nodes apart distance, get it from the table,
        # if (localNode > cursor and localNode - cursor > 3) or \
        #         (localNode < cursor and (int(N) - cursor) + localNode > 3) or retrieve_mode == 'table':
        if aliveNessTable.get(str(cursor)) >= 0:
            return cursor
        Print.print_("Searching for Node[table]:  " + str(cursor) +
                     ", Status: " + str(aliveNessTable.get(str(cursor))),
                     Print.AvailabilityAndConsistency, local_node)



        # else:
        #     wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), cursor)
        #     response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PING)
        #     Print.print_("Searched for node "+ str(cursor) \
        #         + " and received response: "+ Response.print_response(response_code) + "\n",
        #                  Print.AvailabilityAndConsistency, localNode)
        #     # If time-out continue, else stop
        #     if response_code == Response.RPNOREPLY:
        #         continue
        #     else:
        #         result = cursor
        #         break

    # return result

# Given a node_id return the first alive successor
def successor(local, retrieve_mode="ping"):
    # print "successor for: " + str(local) + ", where the origin is: " + str(local)
    cursor = local_node = int(local)
    # origin = int(local_node)
    # cursor = local_node
    while True:
        # decrement
        cursor = prev(cursor)

        # If Im the only node in the network then break and return the current node_id
        if cursor == local_node:
            result = local_node
            # print "Loop stop: " + str(cursor)
            break


        # Echo-reply
        # ToDo if distance is more than 3 just check the local table,
        # For distance > 3 Check if the cursor in the aliveness table first. If not alive, to Try to PING the cursor
        if (local_node > cursor and local_node - cursor > 3) or \
                (local_node < cursor and (int(N) - cursor) + local_node > 3) or retrieve_mode == 'table':
                Print.print_("Searching for Node[table]:  " + str(cursor) +
                            ", Status: " + str(aliveNessTable.get(str(cursor))),
                             Print.AvailabilityAndConsistency, local_node)
                # Give it some time to populate the table
                time.sleep(.2)
                if aliveNessTable.get(str(cursor)) >= 0:
                    return cursor

        else:
            wire_obj = wire.Wire(int(N), local_node, mode, "main")
            Print.print_("Searching for Node[PING]:  " + str(cursor), Print.AvailabilityAndConsistency, local_node)
            wire_obj.send_request(Command.PING, "Anykey", 0, "", threading.currentThread(), cursor)
            response_code, value = wire_obj.receive_reply(threading.currentThread(), Command.PING)
            # print "Response: "+ Response.print_response(response_code)

            # If time-out continue, else stop
            if response_code == Response.RPNOREPLY:
                continue
            else:
                result = cursor
                break
    return result


def predecessor(local, retrieve_mode="ping"):
    # print "predecessor for: " + str(local) + ", where the origin is: " + str(local)
    cursor = local_node = int(local)

    while True:
        # increment
        cursor = next(cursor)

        # If Im the only node in the network then break and return the current node_id
        if cursor == local_node:
            result = local_node
            # print "Loop stop: " + str(cursor)
            break

        # Echo-reply
        # To Do if distance is more than 3 just check the local table,
        # For distance > 3 Check if the cursor in the aliveness table first. If not alive, to Try to PING the cursor
        if (cursor > local_node  and cursor - local_node > 3) or \
                (cursor < local_node and (int(N) - local_node) + cursor > 3) or retrieve_mode == 'table':
                Print.print_("Searching for Node[table]:  " + str(cursor) +
                            ", Status: " + str(aliveNessTable.get(str(cursor))),
                             Print.AvailabilityAndConsistency, local_node)
                # Give it some time to populate the table
                time.sleep(.2)
                if aliveNessTable.get(str(cursor)) >= 0:
                    return cursor

        else:
            wire_obj = wire.Wire(int(N), local_node, mode, "main")
            Print.print_("Searching for Node[PING]:  " + str(cursor), Print.AvailabilityAndConsistency, local_node)
            wire_obj.send_request(Command.PING, "Anykey", 0, "", threading.currentThread(), cursor)
            response_code, value = wire_obj.receive_reply(threading.currentThread(), Command.PING)
            # print "Response: "+ Response.print_response(response_code)

            # If time-out continue, else stop
            if response_code == Response.RPNOREPLY:
                continue
            else:
                result = cursor
                break
    return result


def join_successor():  # To get the local node keys. send to 1 sucessor (i.e. 1 send to 0)
    local_node = int(hashedKeyModN)
    successor_ = successor(local_node)  # search by node id
    if successor_ != local_node:  # else its only me in the network
        Print.print_("successor found: "+ str(successor_) + "\n", Print.AvailabilityAndConsistency, local_node)
        wire_obj = wire.Wire(int(N), local_node, mode, "main")
        wire_obj.send_request(Command.JOIN_SUCCESSOR, "anyKey", len(str(local_node)), str(local_node)
                              , threading.currentThread(), successor_)
        response_code, value = wire_obj.receive_reply(threading.currentThread(), Command.JOIN_SUCCESSOR)

    Print.print_("Join SUCCESSOR synchronization is finished"+ "\n"\
         ,Print.AvailabilityAndConsistency, local_node)


def join_predecessor():  # To get the replicated keys from others #TODO send 3 predessors (i.e. 1 send to 2, 3, and 4)
    local_node = int(hashedKeyModN)

    update_predecessor_list()
    unique_set = set(predecessor_list)
    for x in unique_set:
        if x != int(hashedKeyModN) and x != -1:
            wire_obj = wire.Wire(int(N), local_node, mode, "main")
            wire_obj.send_request(Command.JOIN_PREDECESSOR, "anyKey", len(str(local_node)), str(local_node)
                                  , threading.currentThread(), x)
            response_code, value = wire_obj.receive_reply(threading.currentThread(), Command.JOIN_PREDECESSOR)
            time.sleep(2)
    # predecessor_1 = predecessor(local_node)  # search by node id
    # if predecessor_1 != local_node:  # else its only me in the network
    #     Print.print_("predecessor_ found: "+ str(predecessor_1) + "\n", Print.AvailabilityAndConsistency, local_node)
    #     wire_obj = wire.Wire(int(N), local_node, mode, "main")
    #     wire_obj.send_request(Command.JOIN_PREDECESSOR, "anyKey", len(str(local_node)), str(local_node)
    #                           , threading.currentThread(), predecessor_1)
    #     response_code, value = wire_obj.receive_reply(threading.currentThread(), Command.JOIN_PREDECESSOR)
    # time.sleep(2)
    # predecessor_2 = predecessor(predecessor_1)  # search by node id
    # if predecessor_2 != local_node:  # else its only me in the network
    #     Print.print_("predecessor_ found: "+ str(predecessor_2) + "\n", Print.AvailabilityAndConsistency, local_node)
    #     wire_obj = wire.Wire(int(N), local_node, mode, "main")
    #     wire_obj.send_request(Command.JOIN_PREDECESSOR, "anyKey", len(str(local_node)), str(local_node)
    #                           , threading.currentThread(), predecessor_2)
    #     response_code, value = wire_obj.receive_reply(threading.currentThread(), Command.JOIN_PREDECESSOR)
    # time.sleep(2)
    # predecessor_3 = predecessor(predecessor_2)  # search by node id
    # if predecessor_3 != local_node:  # else its only me in the network
    #     Print.print_("predecessor_ found: "+ str(predecessor_3) + "\n", Print.AvailabilityAndConsistency, local_node)
    #     wire_obj = wire.Wire(int(N), local_node, mode, "main")
    #     wire_obj.send_request(Command.JOIN_PREDECESSOR, "anyKey", len(str(local_node)), str(local_node)
    #                           , threading.currentThread(), predecessor_3)
    #     response_code, value = wire_obj.receive_reply(threading.currentThread(), Command.JOIN_PREDECESSOR)

    Print.print_("Join PREDECESSOR synchronization is finished"+ "\n"\
         ,Print.AvailabilityAndConsistency, local_node)

# Get the last three healthy adjacent
successor_list = [-1, -1, -1]
def update_successor_list():
    local_node = int(hashedKeyModN)
    successor_list[0] = successor(local_node, 'table')
    if successor_list[0] != -1 and successor_list[0] != int(hashedKeyModN):
        successor_list[1] = successor(successor_list[0], 'table')
    if successor_list[1] != -1 and successor_list[0] != int(hashedKeyModN):
        successor_list[2] = successor(successor_list[1], 'table')

# Get the last three healthy adjacent
predecessor_list = [-1, -1, -1]
def update_predecessor_list():
    local_node = int(hashedKeyModN)
    predecessor_list[0] = predecessor(local_node, 'ping')
    if predecessor_list[0] != -1 and predecessor_list[0] != int(hashedKeyModN):
        predecessor_list[1] = predecessor(predecessor_list[0], 'ping')
    if predecessor_list[1] != -1 and predecessor_list[1] != int(hashedKeyModN):
        predecessor_list[2] = predecessor(predecessor_list[1], 'ping')


def replicate(command, key, value=""):
    # global successor_list
    print "replicating: "
    if command == Command.PUT:
        # put on the next three nodes
        update_successor_list()
        unique_set = set(successor_list)
        for x in unique_set:
            if x != int(hashedKeyModN) and x != -1:
                wireObj_replicate.send_request(Command.REPLICATE_PUT, key, len(value), value, threading.currentThread(), x)
                response_code, value_ = wireObj_replicate.receive_reply(threading.currentThread(), Command.REPLICATE_PUT)
                # if response_code != Response.SUCCESS  # Check aliveness and dix the successor list
                # There is no nodes in the network"
            # else:
                # print "No successors found. No replicaiton. " + str(x)
                # No replications then!
    elif command == Command.REMOVE:
        # remove on the next three nodes
        update_successor_list()
        for x in successor_list:
            if successor_list != int(hashedKeyModN):
                wireObj_replicate.send_request(Command.REPLICATE_REMOVE, key, len(value), value, threading.currentThread(), x)
                response_code, value = wireObj_replicate.receive_reply(threading.currentThread(), Command.REPLICATE_REMOVE)
                # if response_code != Response.SUCCESS  # Check aliveness and dix the successor list
                # There is no nodes in the network"
            else:
                print "No successors found. No replicaiton"
                # No replications then!


def off_load_get_thread(key, sender_addr, cur_thread):
    response, value = off_load_get(key)
    value_to_send = value
    wireObj.send_reply(sender_addr, key, response, len(value_to_send), value_to_send, cur_thread, Command.GET)


def off_load_get(key):
    if aliveNessTable.get(str(hash(key) % int(N))) >= 0:
        successor_ = hash(key) % int(N)
    else:
        successor_ = search(key, "table")
    # print "successor_: " + str(successor_) + ",str(aliveNessTable.get(str(hash(key) % int(N)))):" + str(aliveNessTable.get(str(hash(key) % int(N))))
    if successor_ != int(hashedKeyModN):  # not the local node
        wireObj.send_request(Command.GET_HINTED, key, 0, "", threading.currentThread(), successor_)
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.GET)

        if response_code != Response.SUCCESS and response_code != Response.NONEXISTENTKEY:  # NOREPLY
            # PING it, if dead. Declare dead and call recursively
            # wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), successor_)
            # response_code_, value_ = wireObj.receive_reply(threading.currentThread(), Command.PING)
            # if response_code_ != Response.SUCCESS:  # Declare dead
                # print "recursive find" + ", successor_:" + str(successor_) + ", aliveNessTable.get(successor_)" + \
                #     str(aliveNessTable.get(successor_))
                # aliveNessTable.remove(str(successor_))  # May be penalize in the negative to solve teh later msgs on the way
            aliveNessTable.put(str(successor_), -6)
            response_code, value = off_load_get(key)
            # else:
            #     response_code, value = off_load_get(key)
        else:
            Print.print_("Value:" + str(value),Print.Main, hashedKeyModN)

    else:  # the local node
        response_code, value = try_to_get(key)

    return response_code, value


def off_load_put_thread(key, value, sender_addr, cur_thread):
    response = off_load_put(key, value)
    wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.PUT)


def off_load_put(key, value):
    if aliveNessTable.get(str(hash(key) % int(N))) >= 0:
        successor_ = hash(key) % int(N)
    else:
        successor_ = search(key, "table")

    # if successor_ != -2:
    if successor_ != int(hashedKeyModN):  # not the local node
        # print "remote"

        wireObj.send_request(Command.PUT_HINTED, key, len(value), value, threading.currentThread(), successor_)
        response_code, value_ = wireObj.receive_reply(threading.currentThread(), Command.PUT)

        # SUDDEN DEATH OR SUDDEN JOIN
        if response_code != Response.SUCCESS:  # probably dead but not yet propagated, Workaround procedure
            # PING it, if dead. Declare dead and call recursively
            # wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), successor_)
            # response_code_, value_ = wireObj.receive_reply(threading.currentThread(), Command.PING)
            # if response_code_ != Response.SUCCESS:  # Declare dead
            print "recursive find"
                # aliveNessTable.remove(successor_)
            aliveNessTable.put(str(successor_), -6)
            response_code = off_load_put(key, value)
            # else:
            #     response_code = off_load_put(key, value)

    else:  # local
        # print "local"
        response_code = try_to_put(key, value)
        # replicate(Command.PUT, key, value)
        replicate_put_thread = threading.Thread(target=replicate, args=(Command.PUT, key, value))
        replicate_put_thread.start()
    return response_code


def off_load_remove_thread(key, sender_addr, cur_thread):
    response = off_load_remove(key)
    wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REMOVE)


def off_load_remove(key):
    if aliveNessTable.get(str(hash(key) % int(N))) >= 0:
        successor_ = hash(key) % int(N)
    else:
        successor_ = search(key, "table")

    if successor_ != int(hashedKeyModN):  # not the local node
        wireObj.send_request(Command.REMOVE_HINTED, key, 0, "", threading.currentThread(), successor_)
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.REMOVE)

        # SUDDEN DEATH probably dead but not yet propagated, Workaround procedure
        if response_code != Response.SUCCESS and response_code != Response.NONEXISTENTKEY:
                # PING it, if dead. Declare dead and call recursively
                # wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), successor_)
                # response_code_, value_ = wireObj.receive_reply(threading.currentThread(), Command.PING)
                # if response_code_ != Response.SUCCESS:  # Declare dead
                    # aliveNessTable.remove(successor_)
                aliveNessTable.put(str(successor_), -6)
                response_code = off_load_remove(key)
                # else:
                #     response_code = off_load_remove(key)

    else:  # local
        response_code = try_to_remove(key)
        replicate_remove_thread = threading.Thread(target=replicate, args=(Command.REMOVE, key))
        replicate_remove_thread.start()
    return response_code


class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
        pass


class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        #         # data = self.request[0].strip()
        #         # socket = self.request[1]
        #         # print("{} wrote: ".format(self.client_address[0]))
        #         # print(data)
        #         # socket.sendto(data.upper(), self.client_address)
        #         cur_thread = threading.currentThread()

        # while True:
        #             command, key, value_length, value, sender_addr = wireObj.receive_request(hashedKeyModN, cur_thread, self)
        receive_request(self)


def clean_up_replicated_keys():
    while True:
        time.sleep(10)
        for key, value in kvTable.hashTable.items():
            node_id = hash(key) % int(N)
            if node_id != int(hashedKeyModN):
                s = get_direct_successor(key)

                if int(hashedKeyModN) not in s \
                    and aliveNessTable.get(str(s[0])) >= 0\
                    and aliveNessTable.get(str(s[1])) >= 0\
                    and aliveNessTable.get(str(s[2])) >= 0:
                    Print.print_("clean_up_replicated_keys" + ",Key: " + key + ",Node: " + str(node_id) + ", get_direct_successor: " + str(s), Print.Cleaning_keys, hashedKeyModN, threading.currentThread())
                    # wireObj_replicate.send_request(Command.REPLICATE_PUT, key, len(value), value, threading.currentThread(), s[2])
                    # response_code_2, value_ = wireObj_replicate.receive_reply(threading.currentThread(), Command.REPLICATE_PUT)
                    # wireObj_replicate.send_request(Command.REPLICATE_PUT, key, len(value), value, threading.currentThread(), s[1])
                    # response_code_1, value_ = wireObj_replicate.receive_reply(threading.currentThread(), Command.REPLICATE_PUT)
                    # wireObj_replicate.send_request(Command.REPLICATE_PUT, key, len(value), value, threading.currentThread(), s[0])
                    # response_code_0, value_ = wireObj_replicate.receive_reply(threading.currentThread(), Command.REPLICATE_PUT)
                    # If receive less than 3 responses, keep it
                    # if response_code_2 == Response.SUCCESS and response_code_1 == Response.SUCCESS and response_code_0 == Response.SUCCESS:
                    kvTable.remove(key)
                    Print.print_("Key is deleted. All successors are up and alive", Print.Cleaning_keys, hashedKeyModN, threading.currentThread())
                # else:
                #     print "Key is not deleted"


# Direct successor are the most closed ones
def get_direct_successor(key, node_id=""):
    s = [-1, -1, -1]
    if node_id == "":
        node_id = hash(key) % int(N)

    s[0] = prev(node_id)
    s[1] = prev(s[0])
    s[2] = prev(s[1])
    # print "s: "+ str(s)
    return s

# def distance_node_to_key(node_id, key):
#     if node_id - hash(key) > int(N)/2:
#         return int(N) - (node_id - hash(key) > int(N))
#     else:
#         return node_id - hash(key)
def receive_request_replicate_only(handler=""):
    while True:
        cur_thread = threading.currentThread()
        command, key, value_length, value, sender_addr = wireObj_replicate.receive_request(hashedKeyModN, cur_thread, handler)
        if command == Command.REPLICATE_PUT:
            response = try_to_put(key, value)
            wireObj_replicate.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REPLICATE_PUT)
        elif command == Command.REPLICATE_REMOVE:
            response = try_to_remove(key)
            wireObj_replicate.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REPLICATE_REMOVE)

def receive_request_push_alive_only(handler=""):
    global contaminated
    while True:
        cur_thread = threading.currentThread()
        command, key, value_length, value, sender_addr = wireObj_push_alive.receive_request(hashedKeyModN, cur_thread, handler)
        if command == Command.PUSH:
            value_piggybacking = aliveNessTable.get_list_of_alive_keys()
            value_piggybacking = ",".join(value_piggybacking)
            wireObj_push_alive.send_reply(sender_addr, key, Response.SUCCESS, len(value_piggybacking), value_piggybacking, cur_thread, Command.PUSH)
            # Send msg Epidemicly; anti-antrpoy
            if int(key) != int(hashedKeyModN):
                increment_soft_state(key)
                list_of_alive_nodes = value.split(',')
                update_incoming(list_of_alive_nodes)

                if not contaminated:
                    epidemic_anti_antropy(key)
                    contaminated = True

        elif command == Command.ALIVE:
            # Biggy back reply
            value_piggybacking = aliveNessTable.get_list_of_alive_keys()
            value_piggybacking = ",".join(value_piggybacking)
            wireObj_push_alive.send_reply(sender_addr, key, Response.SUCCESS, len(value_piggybacking), value_piggybacking, cur_thread, Command.ALIVE)

            list_of_alive_nodes = value.split(',')
            update_incoming(list_of_alive_nodes)
            if int(key) != int(hashedKeyModN):
                increment_soft_state(key)

            if not contaminated:
                epidemic_anti_antropy(key)
                contaminated = True


def if_local_have_join_as_successor(join_id):
    join_id = int(join_id)
    s = get_direct_successor("any", int(hashedKeyModN)) # should not be direct. should be any #TODO
    if join_id in s:
        return True
    else:
        return False


def if_join_have_local_as_successor(join_id):
    join_id = int(join_id)
    s = get_direct_successor("any", join_id)
    if join_id in s:
        return True
    else:
        return False

# def if_predessor(join_id):
#     join_id = int(join_id)
#     local_id = int(hashedKeyModN)
#     if next(local_id) == join_id:
#         return True
#
#     if aliveNessTable(next(local_id)) is None and next(local_id) < join_id:  # if all in between are dead
#         if_predessor(next(join_id))
#     else:
#         return True

# Single threaded if called from the main, multithreaded if called from ThreadedUDPRequestHandler
contaminated = False
def receive_request(handler=""):
    while True:
        cur_thread = threading.currentThread()
        command, key, value_length, value, sender_addr = wireObj.receive_request(hashedKeyModN, cur_thread, handler)
        if command == Command.PUT:
            offload_thread = threading.Thread(target=off_load_put_thread, args=(key, value, sender_addr, cur_thread))
            offload_thread.start()

            # response = off_load_put(key, value)
            # wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.PUT)

        elif command == Command.PUT_HINTED:
            response = try_to_put(key, value)
            wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.PUT_HINTED)
            replicate_thread = threading.Thread(target=replicate, args=(Command.PUT, key, value))
            replicate_thread.start()

        elif command == Command.GET:
            offload_get_thread = threading.Thread(target=off_load_get_thread, args=(key, sender_addr, cur_thread))
            offload_get_thread.start()
            # response, value = off_load_get(key)
            # value_to_send = value
            # wireObj.send_reply(sender_addr, key, response, len(value_to_send), value_to_send, cur_thread, Command.GET)

        elif command == Command.GET_HINTED:
            response, value_to_send = try_to_get(key)
            wireObj.send_reply(sender_addr, key, response, len(value_to_send), value_to_send, cur_thread, Command.GET)

        elif command == Command.REMOVE:
            offload_remove_thread = threading.Thread(target=off_load_remove_thread, args=(key, sender_addr, cur_thread))
            offload_remove_thread.start()
            # response = off_load_remove(key)
            # wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REMOVE)

        elif command == Command.REMOVE_HINTED:
            response = try_to_remove(key)
            wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REMOVE)
            # replicate(Command.REMOVE, key, value)
            replicate_thread = threading.Thread(target=replicate, args=(Command.REMOVE, key))
            replicate_thread.start()

        elif command == Command.SHUTDOWN:
            response = Response.SUCCESS
            wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.SHUTDOWN)
            os._exit(10)

        elif command == Command.PING:
            response = Response.SUCCESS
            value = "Alive!"
            wireObj.send_reply(sender_addr, key, response, len(value), value, cur_thread, Command.PING)

        elif command == Command.JOIN_SUCCESSOR:
            join_id = int(value)
            wireObj.send_reply(sender_addr, "", Response.SUCCESS, 0, "", cur_thread, Command.JOIN_SUCCESSOR)  # For th join
            # keys_to_be_deleted = []
            for k in kvTable.hashTable:
                distance = int(math.fabs(int(hashedKeyModN) - join_id))
                # if distance == 1 and (hash(k) % int(N) > int(hashedKeyModN) or hash(k) % int(N) == join_id) or \
                #         (distance > 1 and hash(k) % int(N) == join_id) or \
                #                 distance_node_to_key(join_id, k) <= distance_node_to_key(int(hashedKeyModN), k):
                is_join_have_local_as_successor = if_join_have_local_as_successor(join_id)
                if hash(k) % int(N) == join_id:  # and is_join_have_local_as_successor:
                    key_value = kvTable.hashTable[k]
                    wireObj_replicate.send_request(Command.REPLICATE_PUT, k, len(key_value), key_value,
                                         threading.currentThread(), join_id)
                    response_code, value = wireObj_replicate.receive_reply(threading.currentThread(), Command.PUT)
                    # if response_code == Response.SUCCESS:
                    #     keys_to_be_deleted.append(k)
                    # else:
                    #     Print.print_("The joined node is dead for this key" + ", response: " +
                    #                  Response.print_response(response_code), Print.Main, hashedKeyModN)
            # for k in keys_to_be_deleted:
            #     kvTable.remove(k)
        elif command == Command.JOIN_PREDECESSOR:
            join_id = int(value)
            wireObj.send_reply(sender_addr, "", Response.SUCCESS, 0, "", cur_thread, Command.JOIN_SUCCESSOR)  # For th join

            for k in kvTable.hashTable:
                is_local_have_join_as_successor = if_local_have_join_as_successor(join_id)
                if hash(k) % int(N) == int(hashedKeyModN):  # and is_local_have_join_as_successor:
                    key_value = kvTable.hashTable[k]
                    wireObj_replicate.send_request(Command.REPLICATE_PUT, k, len(key_value), key_value,
                                         threading.currentThread(), join_id)
                    response_code, value = wireObj_replicate.receive_reply(threading.currentThread(), Command.PUT)
        else:
            response = Response.UNRECOGNIZED
            wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.PUT)  # no unrecog command


# Increment all the incoming updates.. PUSH
def update_incoming(list_of_alive_nodes):
    global contaminated
    for x in list_of_alive_nodes:  # Increment the status of all alive nodes
        if x is not None and x is not "":
            k, count = x.split(':')
            if int(k) != int(hashedKeyModN) and k != "":
                if aliveNessTable.get(k) is not None:
                    if int(count) > int(aliveNessTable.get(k)):
                        increment_soft_state(k)
                        # print "BONUS!: " + str(k),
                else:  # if does not exist locally, increment!
                    # print "NEW LIFE!!: " + str(k)
                    increment_soft_state(k)


# Increment the soft state
def increment_soft_state(key):
    if aliveNessTable.get(key) is None:
        aliveNessTable.put(key, 0)
    else:
        if int(aliveNessTable.get(key)) + 1 > 3:  # max 3
            aliveNessTable.put(key, 3)
        else:
            aliveNessTable.put(key, int(aliveNessTable.get(key)) + 1)


def epidemic_gossip():
    sum_counter = 0 # Total Alive msgs
    print "epidemic gossip"
    while True:  # Send to log(N) nodes
        print ".",
        counter = 0
        while counter < int(math.log(int(N), 2)):
            randomNode = other_node()
            # print "Iteration: " + str(counter) + "randomNode" + str(randomNode)
            value = aliveNessTable.get_list_of_alive_keys()
            value = ",".join(value)
            wireObj_push_alive.send_request(Command.ALIVE, str(hashedKeyModN), len(value), value,
                                 threading.currentThread(), randomNode, retrials=2)
            response_code, value_biggy = wireObj_push_alive.receive_reply(threading.currentThread(), Command.ALIVE)
            if response_code == Response.SUCCESS:
                increment_soft_state(str(randomNode))
                value_biggy = value_biggy.split(',')
                update_incoming(value_biggy)
            counter += 1
            time.sleep(1)  # not to overwhelm 1 node in small rings
        sum_counter += counter
        # Stop with probability 1/k
        if int(N) >= 10:
            k = 4  # will reach all nodes except .7%
        else:
            k = 2
        probability_to_stop = 1.0 / k
        tmp = random.uniform(0.0, 1.0)
        if tmp < probability_to_stop:
            print "Gossip Stopped with prob (1/k=" + str(k) + "): " + str(tmp) + ". After " + str(sum_counter) + "  ALIVE msgs"
            break


def epidemic_anti_antropy(key):
    counter = 0
    while counter < int(math.log(int(N), 2)):
        # print "Iteration: " + str(counter)
        random_node = other_node(key)
        if key != random_node:
            value = aliveNessTable.get_list_of_alive_keys()
            value = ",".join(value)
            wireObj_push_alive.send_request(Command.PUSH, str(key), len(value), value,
                                 threading.currentThread(), random_node, retrials=2)
            response_code, value_biggy = wireObj_push_alive.receive_reply(threading.currentThread(), Command.PUSH)
            if response_code == Response.SUCCESS:
                increment_soft_state(str(random_node))
                value_biggy = value_biggy.split(',')
                update_incoming(value_biggy)
        counter += 1
        time.sleep(.2)  # not to overwhelm 1 node in small rings


def other_node(sender="-1"):  # exclude sender as well
    tmp = random.randint(0, int(N) - 1)
    # print sender
    if tmp == int(hashedKeyModN) or tmp == int(sender):
        return other_node()
    else:
        return int(tmp)


def i_am_alive_antri_antropy():
    global contaminated
    while True:
        if int(N) > 10:
            r = random.randint(2, 3)  # periodically
        else:
            r = random.randint(2, 5)  # periodically
        time.sleep(3)
        random_node = other_node()
        value = aliveNessTable.get_list_of_alive_keys()
        value = ",".join(value)
        wireObj_push_alive.send_request(Command.PUSH, str(hashedKeyModN),
                             len(value),
                             value,
                             threading.currentThread(), random_node, retrials=2)
        response_code, value_biggy = wireObj_push_alive.receive_reply(threading.currentThread(), Command.PUSH)
        if response_code == Response.SUCCESS:
            increment_soft_state(str(random_node))
            value_biggy = value_biggy.split(',')
            update_incoming(value_biggy)
        contaminated = False


def other_alive_node(sender="-1"):  # exclude sender as well
    if len(aliveNessTable.hashTable) > 0:
        # tmp = random.randint(0, len(aliveNessTable.hashTable) - 1)
        return random.choice(aliveNessTable.hashTable.keys())
    else:
        tmp = random.randint(0, int(N) - 1)
        if tmp == int(hashedKeyModN) or tmp == int(sender):
                return other_alive_node()
        else:
            return int(tmp)


def i_am_alive_small_network():
    while True:
        time.sleep(2)
        # print "i_am_alive_small_network"
        random_node = other_alive_node()
        value = aliveNessTable.get_list_of_alive_keys()
        value = ",".join(value)
        wireObj_push_alive.send_request(Command.PUSH, str(hashedKeyModN),
                             len(value),
                             value,
                             threading.currentThread(), random_node, retrials=2)
        response_code, value_biggy = wireObj_push_alive.receive_reply(threading.currentThread(), Command.PUSH)
        if response_code == Response.SUCCESS:
            increment_soft_state(str(random_node))
            value_biggy = value_biggy.split(',')
            update_incoming(value_biggy)

def i_am_alive_gossip():
        randomNode = other_node()
        wireObj_push_alive.send_request(Command.ALIVE, str(hashedKeyModN), 0, "", threading.currentThread(), randomNode, retrials=2)
        response_code, value = wireObj_push_alive.receive_reply(threading.currentThread(), Command.ALIVE)
        if response_code == Response.SUCCESS:
            increment_soft_state(str(randomNode))


# Decrement the soft state
def decrement_soft_state():
    while True:
        # if int(N) > 10:  # for the 50 nodes
        #     time.sleep(6)
        #     step = 1
        # else:
        time.sleep(2)
        step = 1

        for k in aliveNessTable.hashTable:
            if aliveNessTable.get(k) - step < -1:  # min =-1
                aliveNessTable.put(k, -1)
            else:
                aliveNessTable.put(k, aliveNessTable.get(k) - step)

        # Cleanup -1
        remove = [k for k, v in aliveNessTable.hashTable.items() if v == -1]
        for k in remove: del aliveNessTable.hashTable[k]


def try_to_get(key):
    value_to_send = ("", )
    try:
        value = kvTable.get(key)
        Print.print_("KV[" + str(key) + "]=" + str(kvTable.get(key)), Print.Main, hashedKeyModN)
        if value is None:
            value_to_send = ("", )
            raise KeyError
        else:
            response = Response.SUCCESS
            value_to_send = (value, )
    except KeyError:
        response = Response.NONEXISTENTKEY
    except MemoryError:
        response = Response.OVERLOAD
    except:
        # response = Response.STOREFAILURE
        raise
    return response, value_to_send[0]


def try_to_remove(key):
    try:
        value = kvTable.remove(key)
        if value == "does no exist":
            raise KeyError
        else:
            Print.print_("Removing KV[" + str(key) + "]=" + value, Print.Main, hashedKeyModN)
            response = Response.SUCCESS
    except KeyError:
        response = Response.NONEXISTENTKEY
    except MemoryError:
        response = Response.OVERLOAD
    except:
        response = Response.STOREFAILURE

    return response


def try_to_put(key, value):
    try:
        # Check of the hashtable size before insertions
        # if kvTable.size() > 64000000:
        #     raise Exceptions.OutOfSpaceException()
        # else:
        kvTable.put(key, value)
        Print.print_(" KV[" + str(key) + "]=" + value, Print.Main, hashedKeyModN)
        response = Response.SUCCESS
    except IOError:
        response = Response.OUTOFSPACE
    except Exceptions.OutOfSpaceException:
        response = Response.OUTOFSPACE
    except:
        # response = Response.STOREFAILURE
        raise
    return response


def user_input():
    while True:
        print "\nmain$ [node_id:" + str(hashedKeyModN) + "] Please Enter one of the following:" + "\n" +\
              "     1- Print the local Key-value store:            5- Search for a key:" + "\n" + \
              "     2- Get a value for a key (KV[key]):            6- Shutdown a node by (key/node_id):" + "\n" + \
              "     3- Put a value for a key (KV[key]=value):      7- Ping a node by (key/node_id):" + "\n" + \
              "     4- Remove a key from KV):                      8- Turn debugging msgs ON/OFF" + "\n" + \
              "     9- Print ServerCache                           10- Print Alive nodes" + "\n" + \
              "     11- print successor table                      Other- Exit"

        nb = raw_input('>')
        if nb == "1":
            kvTable._print()
        elif nb == "2":  # GET
            key = raw_input('Main$ Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                response_code, value = try_to_get(key)
            else:  # Not local
                response_code, value = off_load_get(key)
            Print.print_("Response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)

        elif nb == "3":  # PUT
            key = raw_input('Main$ Please enter the key>')
            value = raw_input('Main$ Please enter the value>')
            if hash(key) % int(N) == int(hashedKeyModN):
                response_code = try_to_put(key, value)
                # replicate(Command.PUT, key, value)
                replicate_thread = threading.Thread(target=replicate, args=(Command.PUT, key, value))
                replicate_thread.start()
            else:
                response_code = off_load_put(key, value)
            Print.print_("Response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)

        elif nb == "4":  # remove
            key = raw_input('Main$ Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                response_code = try_to_remove(key)
                # replicate(Command.REMOVE, key)
                replicate_thread = threading.Thread(target=replicate, args=(Command.REMOVE, key))
                replicate_thread.start()
            else:
                response_code = off_load_remove(key)
            Print.print_("response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)
        elif nb == "5":   # search
            key = raw_input('Main$ Please enter the key>')
            output = search(key, "table")
            Print.print_("The Result is: " + str(output), Print.Main, hashedKeyModN)
        elif nb == "6":   # Shutdown
            option = raw_input('Main$ Shutdown by key (y/n)?>')
            if option == "y" or option == "yes":
                key = raw_input('Main$ Please enter the key>')
                # Check if the key is stored locally else send a request
                if hash(key) % int(N) == int(hashedKeyModN):
                    os._exit(10)
                    response_code = Response.SUCCESS
                else:
                    wireObj.send_request(Command.SHUTDOWN, key, 0, "", threading.currentThread(), -1)
                    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.SHUTDOWN)  
                Print.print_("response:" + Response.print_response(response_code),
                             Print.Main, hashedKeyModN)
            else:
                node_id = raw_input('Main$ Please enter the node_id>')
                if int(node_id) == int(hashedKeyModN):
                    os._exit(10)
                    response_code = Response.SUCCESS
                else:
                    wireObj.send_request(Command.SHUTDOWN, "AnyKey", 0, "", threading.currentThread(), node_id)
                    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.SHUTDOWN)  
                Print.print_("response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)
        elif nb == "7":   # Ping
            option = raw_input('Main$ Ping by key (y/n)?>')
            if option == "y" or option == "yes":
                key = raw_input('Main$ Please enter the key>')
                # Check if the key is stored locally else send a request
                if hash(key) % int(N) == int(hashedKeyModN):
                    value = ("Alive!",)
                    response_code = Response.SUCCESS
                else:
                    wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), -1)
                    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PING)  
                Print.print_("response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)
                if response_code == Response.SUCCESS: Print.print_("Reply:" + str(value[0]), Print.Main, hashedKeyModN)
            else:
                node_id = raw_input('Main$ Please enter the node_id>')
                if int(node_id) == int(hashedKeyModN):
                    value = ("Alive!",)
                    response_code = Response.SUCCESS
                else:
                    wireObj.send_request(Command.PING, "AnyKey", 0, "", threading.currentThread(), node_id)
                    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PING)  
                Print.print_("response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)
                if response_code == Response.SUCCESS: Print.print_("Reply:" + str(value[0]), Print.Main, hashedKeyModN)
        elif nb == "8":   # Toggle debugging
            if Print.debug:
                Print.debug = False
            else:
                Print.debug = True
        elif nb == "9":   # Print ServerCache
            wireObj.RequestReplyServer_obj.cache._print()
        elif nb == "10":
            aliveNessTable._print()
        elif nb == "11":
            for x in successor_list:
                print x
        else:
            # sys.exit("Exit normally.")
            os._exit(10)


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv, "", [""])
    N = args[1]
    mode = ""
    number_of_successors = 3
    Print.debug = True
    if len(args) > 2:
        hashedKeyModN = args[2]
        mode = Mode.local
    else:  # planetLab mode
        hashedKeyModN = NodeList.look_up_ip_address()
        if hashedKeyModN == -1:
                Print.print_("The local node ip address is not the node_list_planetLab.txt file",
                             Print.Main, hashedKeyModN)
                os._exit(-1)
        else:
            mode = Mode.planetLab
            print "PlanetLab mode"

    kvTable = HashTable.HashTable("KV", int(N))
    wireObj = wire.Wire(int(N), hashedKeyModN, mode, "main", successor_list)
    wireObj_push_alive = wire.Wire(int(N), hashedKeyModN, mode, "epidemic", successor_list)
    wireObj_replicate = wire.Wire(int(N), hashedKeyModN, mode, "replicate", successor_list)
    aliveNessTable = HashTable.HashTable("AliveNess")

    nodeCommunicationObj = AvailabilityAndConsistency.NodeCommunication(int(N), mode)

    multiThreadUDPServer = False
    if not multiThreadUDPServer:  # Single threaded UDP server
        receiveThread = threading.Thread(target=receive_request)
        receiveThread.start()

        receive_request_push_alive_only_Thread = threading.Thread(target=receive_request_push_alive_only)
        receive_request_push_alive_only_Thread.start()

        receive_request_replicate_only_Thread = threading.Thread(target=receive_request_replicate_only)
        receive_request_replicate_only_Thread.start()

    else:  # multiThreaded
        ip_port = NodeList.look_up_node_id(hashedKeyModN, mode)
        # MULTI-THREADED SERVER
        if mode == Mode.planetLab:
            udp_server = ThreadedUDPServer((NodeList.get_ip_address(ip_port.split(':')[0]),
                                            int(ip_port.split(':')[1])), ThreadedUDPRequestHandler)
        else:
            udp_server = ThreadedUDPServer((ip_port.split(':')[0], int(ip_port.split(':')[1])), ThreadedUDPRequestHandler)
        udp_thread = threading.Thread(target=udp_server.serve_forever)
        udp_thread.start()

    # nodeCommunicationObj.join(int(hashedKeyModN), aliveNessTable)  # call joining procedure
    join_successor()  # call joining procedure
    time.sleep(1.5)
    join_predecessor()  # call joining procedure

    time.sleep(1)

    # #  Aliveness thread anti-antropy will run periodically
    iAmAliveAntriAntropyThread = threading.Thread(target=i_am_alive_antri_antropy)
    iAmAliveAntriAntropyThread.start()

    i_am_alive_small_network = threading.Thread(target=i_am_alive_small_network)
    i_am_alive_small_network.start()

    # #  Aliveness-cleaning thread
    aliveNessCleaning = threading.Thread(target=decrement_soft_state)
    aliveNessCleaning.start()

    # Aliveness thread -Gossip ONLY once on startup
    iAmAliveGossipThread = threading.Thread(target=epidemic_gossip)
    iAmAliveGossipThread.start()

    # User input thread
    # if mode != Mode.planetLab:
    userInputThread = threading.Thread(target=user_input)
    userInputThread.start()


    clean_up_replicated_keys_thread = threading.Thread(target=clean_up_replicated_keys)
    clean_up_replicated_keys_thread.start()