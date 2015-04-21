__author__ = 'Owner'
import wire

import Command
import Response
import Print
import threading
import time
import settings

# class NodeCommunication:
#     N = 0
#     mode = ""
#     local_node = -1
# def __init__(numberOfNodes, mode, local_node):
#     settings.N = numberOfNodes
#     settings.mode = mode
#     settings.hashedKeyModN = local_node
    # settings.aliveNessTable = settings.aliveNessTable
# Given a key, the local nodeID of the first alive node is returned
# Unless if it is a key the belongs to the local nodeID then return the local node id
# The returned nodeID may or may not contain the specified key.
# Use the returned nodeID to call subsequent operations.
# Return: 'cursor' if you find a successor other than yourself
# Return: '-2' if the local node is the successor or if you are only alive node in the network
# TODO modify the search to use the aliveness table
def prev_node(key):
    if key == 0:
        return int(settings.N) - 1
    else:
        return key - 1

def next_node(cursor):
    if cursor == int(settings.N) - 1:
        return 0
    else:
        return cursor + 1


def search(key, retrieve_mode="ping"): # TO-Do create class settings.aliveNessTable
    local_node = int(settings.hashedKeyModN)
    cursor = hash(key) % int(settings.N)

    # Key Locally Stored - Preliminary check to see if you are the node the key should be stored on.
    if cursor == local_node:
        Print.print_("Local Key" + "\n",
                     Print.AvailabilityAndConsistency, local_node, threading.currentThread())
        return local_node

    # cursor = hashedNodeID           # Cursor goes through the range of nodes in our system
    while True:
        if cursor == local_node:
            print "stop: " + str(cursor)
            return local_node

        # point cursor to the prev node
        cursor = prev_node(cursor)

        # After 3 nodes apart distance, get it from the table,
        # if (localNode > cursor and localNode - cursor > 3) or \
        #         (localNode < cursor and (int(N) - cursor) + localNode > 3) or retrieve_mode == 'table':
        if settings.aliveNessTable.get(str(cursor)) >= 0:
            return cursor
        # Print.print_("Searching for Node[table]:  " + str(cursor) +
        #              ", Status: " + str(settings.aliveNessTable.get(str(cursor))),
        #              Print.AvailabilityAndConsistency, local_node, threading.currentThread())



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

def successor(node_id, retrieve_mode="ping"):
    # print "successor for: " + str(local) + ", where the origin is: " + str(local)
    cursor = local_node = int(node_id)
    # origin = int(local_node)
    # cursor = local_node
    while True:
        # decrement
        cursor = prev_node(cursor)

        # If Im the only node in the network then break and return the current node_id
        if cursor == local_node:
            result = local_node
            # print "Loop stop: " + str(cursor)
            break


        # Echo-reply
        # ToDo if distance is more than 3 just check the local table,
        # For distance > 3 Check if the cursor in the aliveness table first. If not alive, to Try to PING the cursor
        if (local_node > cursor and local_node - cursor > 3) or \
                (local_node < cursor and (int(settings.N) - cursor) + local_node > 3) or retrieve_mode == 'table':
                # Print.print_("Searching2 for Node[table]:  " + str(cursor) +
                #             ", Status: " + str(settings.aliveNessTable.get(str(cursor))),
                #              Print.AvailabilityAndConsistency, local_node, threading.currentThread())
                # Give it some time to populate the table
                time.sleep(.2)
                if settings.aliveNessTable.get(str(cursor)) >= 0:
                    return cursor

        else:
            wire_obj = wire.Wire(int(settings.N), local_node, settings.mode, "main")
            # Print.print_("Searching for Node[PING]:  " + str(cursor), Print.AvailabilityAndConsistency, local_node, threading.currentThread())
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
        cursor = next_node(cursor)

        # If Im the only node in the network then break and return the current node_id
        if cursor == local_node:
            result = local_node
            # print "Loop stop: " + str(cursor)
            break

        # Echo-reply
        # To Do if distance is more than 3 just check the local table,
        # For distance > 3 Check if the cursor in the aliveness table first. If not alive, to Try to PING the cursor
        if (cursor > local_node  and cursor - local_node > 3) or \
                (cursor < local_node and (int(settings.N) - local_node) + cursor > 3) or retrieve_mode == 'table':
                # Print.print_("Searching for Node[table]:  " + str(cursor) +
                #             ", Status: " + str(settings.aliveNessTable.get(str(cursor))),
                #              Print.AvailabilityAndConsistency, local_node, threading.currentThread())
                # Give it some time to populate the table
                time.sleep(.2)
                if settings.aliveNessTable.get(str(cursor)) >= 0:
                    return cursor

        else:
            wire_obj = wire.Wire(int(settings.N), local_node, settings.mode, "main")
            # Print.print_("Searching for Node[PING]:  " + str(cursor), Print.AvailabilityAndConsistency, local_node, threading.currentThread())
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
    local_node = int(settings.hashedKeyModN)
    successor_ = successor(local_node, )  # search by node id
    if successor_ != local_node:  # else its only me in the network
        Print.print_("successor found: "+ str(successor_) + "\n", Print.AvailabilityAndConsistency, local_node, threading.currentThread())
        wire_obj = wire.Wire(int(settings.N), local_node, settings.mode, "main")
        wire_obj.send_request(Command.JOIN_SUCCESSOR, "anyKey", len(str(local_node)), str(local_node)
                              , threading.currentThread(), successor_)
        response_code, value = wire_obj.receive_reply(threading.currentThread(), Command.JOIN_SUCCESSOR)

    Print.print_("Join SUCCESSOR synchronization is finished"+ "\n"\
         ,Print.AvailabilityAndConsistency, local_node, threading.currentThread())


def join_predecessor():  # To get the replicated keys from others
    local_node = int(settings.hashedKeyModN)

    update_predecessor_list()
    # unique_set = set(settings.hashedKeyModN)
    unique_set = set(predecessor_list)
    for x in unique_set:
        if int(x) != int(settings.hashedKeyModN) and x != -1:
            # print x
            print int(settings.hashedKeyModN)
            wire_obj = wire.Wire(int(settings.N), local_node, settings.mode, "main")
            wire_obj.send_request(Command.JOIN_PREDECESSOR, "anyKey", len(str(local_node)), str(local_node)
                                  , threading.currentThread(), x)
            response_code, value = wire_obj.receive_reply(threading.currentThread(), Command.JOIN_PREDECESSOR)
            time.sleep(.2)
    Print.print_("Join PREDECESSOR synchronization is finished"+ "\n"\
     ,Print.AvailabilityAndConsistency, local_node, threading.currentThread())

# Get the last three healthy adjacent
# successor_list = [-1, -1]
def update_successor_list():
    local_node = int(settings.hashedKeyModN)
    settings.successor_list[0] = successor(local_node, 'table')
    if settings.successor_list[0] != -1 and settings.successor_list[0] != int(settings.hashedKeyModN):
        settings.successor_list[1] = successor(settings.successor_list[0], 'table')
    # if successor_list[1] != -1 and successor_list[0] != int(hashedKeyModN):
    #     successor_list[2] = successor(successor_list[1], 'table')

# Get the last three healthy adjacent
predecessor_list = [-1, -1]
def update_predecessor_list():
    local_node = int(settings.hashedKeyModN)
    predecessor_list[0] = predecessor(local_node,'ping')
    if predecessor_list[0] != -1 and predecessor_list[0] != int(settings.hashedKeyModN):
        predecessor_list[1] = predecessor(predecessor_list[0],'ping')
    # if predecessor_list[1] != -1 and predecessor_list[1] != int(hashedKeyModN):
    #     predecessor_list[2] = predecessor(predecessor_list[1], 'ping')


# Direct successor are the most closed ones
def get_direct_successor(key, node_id=""):
    s = [-1, -1]
    if node_id == "":
        node_id = hash(key) % int(settings.N)

    s[0] = prev_node(node_id)
    s[1] = prev_node(s[0])
    # s[2] = prev(s[1])
    # print "s: "+ str(s)
    return s

def if_local_have_join_as_successor(join_id):
    join_id = int(join_id)
    s = get_direct_successor("any", int(settings.hashedKeyModN)) # should not be direct. should be any #TODO
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