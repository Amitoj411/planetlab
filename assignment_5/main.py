__author__ = 'Owner'
import ring
import wire
import getopt
import sys
import threading
import Command
import Response
import os
import AvailabilityAndConsistency
import time
import NodeList
import Mode
import Print
# import sys
import Exceptions
import SocketServer
import math


lock = threading.RLock()


def off_load_get(key):
    successor = nodeCommunicationObj.search(key, hashedKeyModN)
    if successor != -2:
        # Print.print_ "The Key Doesn't exist on the network, will return current node"
        if successor != int(hashedKeyModN):  # not the local node
            wireObj.send_request(Command.GET, key, 0, "", successor)
            response_code, value = wireObj.receive_reply()  # We are not sending the TA
            value = value[0]
            if response_code == Response.SUCCESS: Print.print_("Value:" + str(value),
                                                               Print.Main, hashedKeyModN)
        else:  # the local node
            response_code, value = try_to_get(key)
    else:
        response_code, value = try_to_get(key)
        if response_code != Response.SUCCESS:
            response_code = Response.NoExternalAliveNodes
            # value = ("",)
            value = ""
    # Print.print_("Response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)
    return response_code, value


def off_load_put(key, value_):
    successor = nodeCommunicationObj.search(key, hashedKeyModN)
    if successor != -2:
        Print.print_("$main: Next alive:" + str(successor), Print.Main, hashedKeyModN)
        if successor != int(hashedKeyModN):  # not the local node
            wireObj.send_request(Command.PUT, key, len(value_), value_, successor)
            response_code, value = wireObj.receive_reply()  # We are sending the TA!
        else:  # local
            response_code = try_to_put(key, value_)
            # Replication here as well
            replicate(Command.PUT, key, value_)
    else:  # There is no nodes in the network"
        response_code = try_to_put(key, value_)
        # No replications then!
    return response_code


def off_load_remove(key):
    successor = nodeCommunicationObj.search(key, hashedKeyModN)
    if successor != -2:
        Print.print_("$main: Next alive:" + str(successor), Print.Main, hashedKeyModN)
        if successor != int(hashedKeyModN):  # not the local node
            wireObj.send_request(Command.REMOVE, key, 0, "", successor)
            response_code, value_ = wireObj.receive_reply()  # We are not sending the TA
        else:  # local
            response_code = try_to_remove(key)
            replicate(Command.REMOVE, key)
    else:
        response_code = try_to_remove(key)
        if response_code != Response.SUCCESS:
            response_code = Response.NoExternalAliveNodes
    return response_code


class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
        pass


class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        cur_thread = threading.current_thread()

        # def receive_request():
        while True:
            command, key, value_length, value, sender_addr = wireObj.receive_request(hashedKeyModN, self, cur_thread)
            if command == Command.PUT:
                response = off_load_put(key, value)
                wireObj.send_reply(sender_addr, key, response, 0, "")

            elif command == Command.REPLICATE_PUT:
                response = try_to_put(key, value)
                wireObj.send_reply(sender_addr, key, response, 0, "")

            elif command == Command.GET:
                response, value = off_load_get(key)
                value_to_send = value

                wireObj.send_reply(sender_addr, key, response, len(value_to_send), value_to_send)

            elif command == Command.REMOVE:
                response = off_load_remove(key)
                wireObj.send_reply(sender_addr, key, response, 0, "")

            elif command == Command.REPLICATE_REMOVE:
                response = try_to_remove(key)
                wireObj.send_reply(sender_addr, key, response, 0, "")

            elif command == Command.SHUTDOWN:
                response = Response.SUCCESS
                wireObj.send_reply(sender_addr, key, response, 0, "")
                os._exit(10)

            elif command == Command.PING:
                response = Response.SUCCESS
                value = "Alive!"
                wireObj.send_reply(sender_addr, key, response, len(value), value)

            elif command == Command.JOIN:
                join_id = int(value)
                wireObj.send_reply(sender_addr, "", Response.SUCCESS, 0, "")  # For th join
                keys_to_be_deleted = []
                for key in kvTable.hashTable:
                    if hash(key) % int(N) == join_id \
                            or (hash(key) % int(N) < join_id and hash(key) % int(N) < hashedKeyModN) \
                            or (hash(key) % int(N) > join_id):  # ensure joinID is the ID of the predecessor or the upper
                            # space between the joined node and the received node

                        key_value = kvTable.hashTable[key]
                        wireObj.send_request(Command.PUT, key, len(key_value), key_value, join_id)
                        response_code, value = wireObj.receive_reply()
                        if response_code == Response.SUCCESS:
                            keys_to_be_deleted.append(key)
                        else:
                            Print.print_("The joined node is dead for this key" + ", response: " +
                                         Response.print_response(response_code), Print.Main, hashedKeyModN)
                for key in keys_to_be_deleted:
                    kvTable.remove(key)

            else:
                response = Response.UNRECOGNIZED
                wireObj.send_reply(sender_addr, key, response, 0, "")


def try_to_get(key):
    value_to_send = ("", )
    try:
        with lock:
            value = kvTable.get(key)
            Print.print_("KV[" + str(key) + "]=" + kvTable.get(key), Print.Main, hashedKeyModN)
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
        with lock:
            value = kvTable.remove(key)
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
        with lock:
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


def replicate(command, key, value=""):
    print "replicating: "
    if command == Command.PUT:
        # put on the next three nodes
        successor = nodeCommunicationObj.successor(int(hashedKeyModN))
        if successor != -2:
            # Print.print_("$main: Next alive:" + str(successor), Print.Main, hashedKeyModN)
            # if successor != int(hashedKeyModN):  # not the local node
            #     print "It seems an observer send the msg .. replicate at: " + str(successor)
            #     next_to_send = successor
            #     for x in range(0, number_of_successors):
            #         wireObj.send_request(Command.REPLICATE_PUT, key, len(value), value, next_to_send)
            #         response_code, value = wireObj.receive_reply()
            #         next_to_send = next_node(next_to_send)
            # else:  # local
            #     print "Local node; replicate"
            next_to_send = successor
            for x in range(0, number_of_successors):
                wireObj.send_request(Command.REPLICATE_PUT, key, len(value), value, next_to_send)
                response_code, value = wireObj.receive_reply()
                next_to_send = next_node(next_to_send)
        else:  # There is no nodes in the network"
            print "No successor found 1"
            # No replications then!
    elif command == Command.REMOVE:
        # remove on the next three nodes
        successor = nodeCommunicationObj.successor(int(hashedKeyModN))
        if successor != -2:
            next_to_send = successor
            for x in range(0, number_of_successors):
                wireObj.send_request(Command.REPLICATE_REMOVE, key, len(value), value, next_to_send)
                response_code, value = wireObj.receive_reply()
                next_to_send = next_node(next_to_send)
        else:  # There is no nodes in the network"
            print "No successor found 2"
            # No replications then!


def next_node(x):
    if x - 1 < 0:
        return int(N) - 1
    else:
        return (x - 1) % int(N)


def user_input():
    while True:
        print "\nmain$ [node_id:" + str(hashedKeyModN) + "] Please Enter one of the following:" + "\n" +\
              "     1- Print the local Key-value store:            5- Search for a key:" + "\n" + \
              "     2- Get a value for a key (KV[key]):            6- Shutdown a node by (key/node_id):" + "\n" + \
              "     3- Put a value for a key (KV[key]=value):      7- Ping a node by (key/node_id):" + "\n" + \
              "     4- Remove a key from KV):                      8- Turn debugging msgs ON/OFF" + "\n" + \
              "     9- Exit"

        nb = raw_input('>')
        if nb == "1":
            kvTable._print()
        elif nb == "2":  # GET
            key = raw_input('Main$ Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                response_code, value = try_to_get(key)
                # replicate(Command.GET, key)
            else:  # Not local
                response_code, value = off_load_get(key)
            Print.print_("Response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)

        elif nb == "3":  # PUT
            key = raw_input('Main$ Please enter the key>')
            value = raw_input('Main$ Please enter the value>')
            if hash(key) % int(N) == int(hashedKeyModN):
                response_code = try_to_put(key, value)
                # Replication should be here: up to three nodes and that is it
                replicate(Command.PUT, key, value)
            else:
                response_code = off_load_put(key, value)
            Print.print_("Response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)

        elif nb == "4":  # remove
            key = raw_input('Main$ Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                response_code = try_to_remove(key)
                # replicate(Command.REMOVE, key)
                replicate(Command.REMOVE, key)
            else:
                response_code = off_load_remove(key)
            Print.print_("response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)
        elif nb == "5":   # search
            key = raw_input('Main$ Please enter the key>')
            output = nodeCommunicationObj.search(key, hashedKeyModN)
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
                    wireObj.send_request(Command.SHUTDOWN, key, 0, "", -1)
                    response_code, value = wireObj.receive_reply()  # We are not sending the TA
                Print.print_("response:" + Response.print_response(response_code),
                             Print.Main, hashedKeyModN)
            else:
                node_id = raw_input('Main$ Please enter the node_id>')
                if int(node_id) == int(hashedKeyModN):
                    os._exit(10)
                    response_code = Response.SUCCESS
                else:
                    wireObj.send_request(Command.SHUTDOWN, "AnyKey", 0, "", node_id)
                    response_code, value = wireObj.receive_reply()  # We are not sending the TA
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
                    wireObj.send_request(Command.PING, key, 0, "", -1)
                    response_code, value = wireObj.receive_reply()  # We are not sending the TA
                Print.print_("response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)
                if response_code == Response.SUCCESS: Print.print_("Reply:" + str(value[0]), Print.Main, hashedKeyModN)
            else:
                node_id = raw_input('Main$ Please enter the node_id>')
                if int(node_id) == int(hashedKeyModN):
                    value = ("Alive!",)
                    response_code = Response.SUCCESS
                else:
                    wireObj.send_request(Command.PING, "AnyKey", 0, "", node_id)
                    response_code, value = wireObj.receive_reply()  # We are not sending the TA
                Print.print_("response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)
                if response_code == Response.SUCCESS: Print.print_("Reply:" + str(value[0]), Print.Main, hashedKeyModN)
        elif nb == "8":   # Toggle debugging
            if Print.debug:
                Print.debug = False
            else:
                Print.debug = True
        else:
            # sys.exit("Exit normally.")
            os._exit(10)


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv, "", [""])
    N = args[1]
    mode = ""
    Print.debug = True
    number_of_successors = int(math.floor(math.log(int(N))))

    if len(args) > 2:
        hashedKeyModN = args[2]
        mode = Mode.local
    else:  # planetLab mode
        hashedKeyModN = NodeList.look_up_ip_address()
        if hashedKeyModN == -1:
                Print.print_("The local node ip address is not the node_list_planetLab.txt file", Print.Main, hashedKeyModN)
                os._exit(-1)
        else:
            mode = Mode.planetLab
            print "PlanetLab mode"


    kvTable = ring.Ring()
    wireObj = wire.Wire(int(N), hashedKeyModN, mode)

    nodeCommunicationObj = AvailabilityAndConsistency.NodeCommunication(int(N), mode, number_of_successors)

    # receiveThread = threading.Thread(target=receive_request)
    # receiveThread.start()
    ip_port = NodeList.look_up_node_id(hashedKeyModN, mode)
    udp_server = ThreadedUDPServer((ip_port.split(':')[0], int(ip_port.split(':')[1])), ThreadedUDPRequestHandler)
    udp_thread = threading.Thread(target=udp_server.serve_forever)
    udp_thread.start()
    # print("UDP serving at port", ip_port[1])

    nodeCommunicationObj.join(int(hashedKeyModN))  # call joining procedure

    time.sleep(1.5)

    userInputThread = threading.Thread(target=user_input)
    userInputThread.start()