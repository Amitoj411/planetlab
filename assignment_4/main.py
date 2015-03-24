from __future__ import with_statement # 2.5 only
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
import Mode
import Print
import Exceptions
import SocketServer
import NodeList
import HashTable
import math
import random


def off_load_get(key):
    if aliveNessTable.get(str(hash(key) % int(N))) >= 0:
        successor = hash(key) % int(N)
    else:
        successor = nodeCommunicationObj.search(key, hashedKeyModN, aliveNessTable)

    if successor != -2:
        # Print.print_ "The Key Doesn't exist on the network, will return current node"
        if successor != int(hashedKeyModN):  # not the local node
            wireObj.send_request(Command.GET_HINTED, key, 0, "", threading.currentThread(), successor)
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.GET)

            if response_code != Response.SUCCESS and response_code != Response.NONEXISTENTKEY:
                # PING it, if dead. Declare dead and call recursively
                wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), successor)
                response_code_, value_ = wireObj.receive_reply(threading.currentThread(), Command.PING)
                if response_code_ != Response.SUCCESS:  # Declare dead
                    aliveNessTable.put(str(successor), -1)
                    response_code, value = off_load_get(key)
            else:
                Print.print_("Value:" + str(value),Print.Main, hashedKeyModN)

        else:  # the local node
            response_code, value = try_to_get(key)
    else:
        response_code, value = try_to_get(key)
        if response_code != Response.SUCCESS:
            response_code = Response.NoExternalAliveNodes
            # value = ("",)
            value = ""
    return response_code, value


def off_load_put(key, value):
    # print("off_load_put {}".format(key))
    if aliveNessTable.get(str(hash(key) % int(N))) >= 0:
        successor = hash(key) % int(N)
    else:
        successor = nodeCommunicationObj.search(key, hashedKeyModN, aliveNessTable)

    if successor != -2:
        Print.print_("$main: Next alive:" + str(successor), Print.Main, hashedKeyModN)
        if successor != int(hashedKeyModN):  # not the local node
            wireObj.send_request(Command.PUT_HINTED, key, len(value), value, threading.currentThread(), successor)
            response_code, value_ = wireObj.receive_reply(threading.currentThread(), Command.PUT)

            if response_code != Response.SUCCESS:  # probably dead but not yet propagated, Workaround procedure
                # PING it, if dead. Declare dead and call recursively
                wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), successor)
                response_code_, value_ = wireObj.receive_reply(threading.currentThread(), Command.PING)
                if response_code_ != Response.SUCCESS:  # Declare dead
                    aliveNessTable.put(str(successor), -1)
                    response_code = off_load_put(key, value)

        else:  # local
            response_code = try_to_put(key, value)
    else:  # There is no nodes in the network"
        response_code = try_to_put(key, value)
    return response_code


def off_load_remove(key):
    if aliveNessTable.get(str(hash(key) % int(N))) >= 0:
        successor = hash(key) % int(N)
    else:
        successor = nodeCommunicationObj.search(key, hashedKeyModN, aliveNessTable)

    if successor != -2:
        Print.print_("$main: Next alive:" + str(successor), Print.Main, hashedKeyModN)
        if successor != int(hashedKeyModN):  # not the local node
            wireObj.send_request(Command.REMOVE_HINTED, key, 0, "", threading.currentThread(), successor)
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.REMOVE)

            # probably dead but not yet propagated, Workaround procedure
            if response_code != Response.SUCCESS and response_code != Response.NONEXISTENTKEY:
                    # PING it, if dead. Declare dead and call recursively
                    wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), successor)
                    response_code_, value_ = wireObj.receive_reply(threading.currentThread(), Command.PING)
                    if response_code_ != Response.SUCCESS:  # Declare dead
                        aliveNessTable.put(str(successor), -1)
                        response_code = off_load_remove(key)

        else:
            response_code = try_to_remove(key)
    else:
        response_code = try_to_remove(key)
        if response_code != Response.SUCCESS:
            response_code = Response.NoExternalAliveNodes
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


# Single threaded if called from the main, multithreaded if called from ThreadedUDPRequestHandler
contaminated = False
def receive_request(handler=""):
    global contaminated
    while True:
        cur_thread = threading.currentThread()
        command, key, value_length, value, sender_addr = wireObj.receive_request(hashedKeyModN, cur_thread, handler)
        if command == Command.PUT:
            response = off_load_put(key, value)
            wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.PUT)

        elif command == Command.PUT_HINTED:
            response = try_to_put(key, value)
            wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.PUT_HINTED)

        elif command == Command.GET:
            response, value = off_load_get(key)
            value_to_send = value
            wireObj.send_reply(sender_addr, key, response, len(value_to_send), value_to_send, cur_thread, Command.GET)

        elif command == Command.GET_HINTED:
            response, value_to_send = try_to_get(key)
            wireObj.send_reply(sender_addr, key, response, len(value_to_send), value_to_send, cur_thread, Command.GET)

        elif command == Command.REMOVE:
            response = off_load_remove(key)
            wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REMOVE)

        elif command == Command.REMOVE_HINTED:
            response = try_to_remove(key)
            wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REMOVE)

        elif command == Command.SHUTDOWN:
            response = Response.SUCCESS
            wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.SHUTDOWN)
            os._exit(10)

        elif command == Command.PING:
            response = Response.SUCCESS
            value = "Alive!"
            wireObj.send_reply(sender_addr, key, response, len(value), value, cur_thread, Command.PING)

        elif command == Command.JOIN:
            join_id = int(value)
            wireObj.send_reply(sender_addr, "", Response.SUCCESS, 0, "", cur_thread, Command.JOIN)  # For th join
            keys_to_be_deleted = []
            for k in kvTable.hashTable:
                if hash(k) % int(N) > int(hashedKeyModN) or hash(k) % int(N) == join_id:
                        # ensure joinID is the ID of the predecessor or the upper
                        # space between the joined node and the received node
                        # or (hash(k) % int(N) < join_id and hash(k) % int(N) < hashedKeyModN) \
                        # or (hash(k) % int(N) > join_id):

                    print hash(k) % int(N)
                    key_value = kvTable.hashTable[k]
                    # print "key_value: " + str(key_value)
                    wireObj.send_request(Command.PUT, k, len(key_value), key_value,
                                         threading.currentThread(), join_id)
                    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)
                    if response_code == Response.SUCCESS:
                        keys_to_be_deleted.append(k)
                    else:
                        Print.print_("The joined node is dead for this key" + ", response: " +
                                     Response.print_response(response_code), Print.Main, hashedKeyModN)
            for k in keys_to_be_deleted:
                kvTable.remove(k)
        elif command == Command.PUSH:
            value_piggybacking = aliveNessTable.get_list_of_alive_keys()
            value_piggybacking = ",".join(value_piggybacking)
            wireObj.send_reply(sender_addr, key, Response.SUCCESS, len(value_piggybacking), value_piggybacking, cur_thread, Command.PUSH)
            # Send msg Epidemicly; anti-antrpoy
            if int(key) != int(hashedKeyModN):
                increamentSoftState(key)
                list_of_alive_nodes = value.split(',')
                update_incoming(list_of_alive_nodes)

                if not contaminated:
                    epidemic_anti_antropy(key)
                    contaminated = True

        elif command == Command.ALIVE:
            # Biggy back reply
            value_piggybacking = aliveNessTable.get_list_of_alive_keys()
            value_piggybacking = ",".join(value_piggybacking)
            wireObj.send_reply(sender_addr, key, Response.SUCCESS, len(value_piggybacking), value_piggybacking, cur_thread, Command.ALIVE)

            list_of_alive_nodes = value.split(',')
            update_incoming(list_of_alive_nodes)
            if int(key) != int(hashedKeyModN):
                increamentSoftState(key)
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
                        increamentSoftState(k)
                        print "BONUS!: " + str(k),
                        # if int(aliveNessTable.get(k)) == 0:
                        #     epidemic_anti_antropy(k)
                else:  # if does not exist locally, increament!
                    print "NEW LIFE!!: " + str(k)
                    increamentSoftState(k)
                    # epidemic_anti_antropy(k)

# Increment the soft state
def increamentSoftState(key):
    if aliveNessTable.get(key) is None:
        aliveNessTable.put(key, 0)
    else:
        if int(aliveNessTable.get(key)) + 1 > 3:  # max 3
            aliveNessTable.put(key, 3)
        else:
            aliveNessTable.put(key, int(aliveNessTable.get(key)) + 1)


def epidemic_gossip():
    sum_counter = 0 # Total Alive msgs
    while True:  # Send to log(N) nodes
        counter = 0
        while counter < int(math.log(int(N), 2)):
            randomNode = otherNode()
            # print "Iteration: " + str(counter) + "randomNode" + str(randomNode)
            value = aliveNessTable.get_list_of_alive_keys()
            value = ",".join(value)
            wireObj.send_request(Command.ALIVE, str(hashedKeyModN), len(value), value,
                                 threading.currentThread(), randomNode, retrials=2)
            response_code, value_biggy = wireObj.receive_reply(threading.currentThread(), Command.ALIVE)  # We are not sending the TA
            if response_code == Response.SUCCESS:
                increamentSoftState(str(randomNode))
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
            print "Gossip Stopped with prob (1/k=" + str(k) + "): " + str(tmp) + ". After " + str(sum_counter) + "  aLIVE msgs"
            break


def epidemic_anti_antropy(key):
    counter = 0
    while counter < int(math.log(int(N), 2)):
        # print "Iteration: " + str(counter)
        randomNode = otherNode(key)
        if key != randomNode:
            value = aliveNessTable.get_list_of_alive_keys()
            value = ",".join(value)
            wireObj.send_request(Command.PUSH, str(key), len(value), value,
                                 threading.currentThread(), randomNode, retrials=2)
            response_code, value_biggy = wireObj.receive_reply(threading.currentThread(), Command.PUSH)
            if response_code == Response.SUCCESS:
                increamentSoftState(str(randomNode))
                value_biggy = value_biggy.split(',')
                update_incoming(value_biggy)
        counter += 1
        time.sleep(.2)  # not to overwhelm 1 node in small rings


def otherNode(sender="-1"):  # exclude sender as well
    tmp = random.randint(0, int(N) - 1)
    # print sender
    if tmp == int(hashedKeyModN) or tmp == int(sender):
        return otherNode()
    else:
        return int(tmp)


def iAmAliveAntriAntropy():
    global contaminated
    while True:
        if int(N) > 10:
            r = random.randint(2, 3)  # periodically
        else:
            r = random.randint(2, 5)  # periodically
        time.sleep(r)
        random_node = otherNode()
        value = aliveNessTable.get_list_of_alive_keys()
        value = ",".join(value)
        wireObj.send_request(Command.PUSH, str(hashedKeyModN),
                             len(value),
                             value,
                             threading.currentThread(), random_node, retrials=2)
        response_code, value_biggy = wireObj.receive_reply(threading.currentThread(), Command.PUSH)
        if response_code == Response.SUCCESS:
            increamentSoftState(str(random_node))
            value_biggy = value_biggy.split(',')
            update_incoming(value_biggy)
        contaminated = False



def iAmAliveGossip():
    # while True:  # TODO remove if not necassary
        randomNode = otherNode()
        wireObj.send_request(Command.ALIVE, str(hashedKeyModN), 0, "", threading.currentThread(), randomNode, retrials=2)
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.ALIVE)
        if response_code == Response.SUCCESS:
            increamentSoftState(str(randomNode))
        # time.sleep(4)


# Decrement the soft state
def decreamentSoftState():
    while True:
        if int(N) > 10:  # for the 50 nodes
            time.sleep(6)
            step = 1
        else:
            time.sleep(3)
            step = 1
        # if len(aliveNessTable.hashTable.) > 0:

        for k in aliveNessTable.hashTable:
            if aliveNessTable.get(k) - step < -1:  # min =-1
                aliveNessTable.put(k, -1)
            else:
                aliveNessTable.put(k, aliveNessTable.get(k) - step)


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
              "     Other- Exit"

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
            else:
                response_code = off_load_put(key, value)
            Print.print_("Response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)

        elif nb == "4":  # remove
            key = raw_input('Main$ Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                response_code = try_to_remove(key)
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
                    wireObj.send_request(Command.SHUTDOWN, key, 0, "", threading.currentThread(), -1)
                    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.SHUTDOWN)  # We are not sending the TA
                Print.print_("response:" + Response.print_response(response_code),
                             Print.Main, hashedKeyModN)
            else:
                node_id = raw_input('Main$ Please enter the node_id>')
                if int(node_id) == int(hashedKeyModN):
                    os._exit(10)
                    response_code = Response.SUCCESS
                else:
                    wireObj.send_request(Command.SHUTDOWN, "AnyKey", 0, "", threading.currentThread(), node_id)
                    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.SHUTDOWN)  # We are not sending the TA
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
                    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PING)  # We are not sending the TA
                Print.print_("response:" + Response.print_response(response_code), Print.Main, hashedKeyModN)
                if response_code == Response.SUCCESS: Print.print_("Reply:" + str(value[0]), Print.Main, hashedKeyModN)
            else:
                node_id = raw_input('Main$ Please enter the node_id>')
                if int(node_id) == int(hashedKeyModN):
                    value = ("Alive!",)
                    response_code = Response.SUCCESS
                else:
                    wireObj.send_request(Command.PING, "AnyKey", 0, "", threading.currentThread(), node_id)
                    response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PING)  # We are not sending the TA
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
        else:
            # sys.exit("Exit normally.")
            os._exit(10)


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv, "", [""])
    N = args[1]
    mode = ""
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


    # kvTable = ring.Ring()
    kvTable = HashTable.HashTable("KV")
    wireObj = wire.Wire(int(N), hashedKeyModN, mode)
    aliveNessTable = HashTable.HashTable("AliveNess")

    nodeCommunicationObj = AvailabilityAndConsistency.NodeCommunication(int(N), mode)

    multiThreadUDPServer = False
    if not multiThreadUDPServer:  #S ingle threaded UDP server
        receiveThread = threading.Thread(target=receive_request)
        receiveThread.start()
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

    nodeCommunicationObj.join(int(hashedKeyModN))  # call joining procedure

    time.sleep(1.5)

    # #  Aliveness thread anti-antropy will run periodically
    iAmAliveAntriAntropyThread = threading.Thread(target=iAmAliveAntriAntropy)
    iAmAliveAntriAntropyThread.start()

    # #  Aliveness-cleaning thread
    aliveNessCleaning = threading.Thread(target=decreamentSoftState)
    aliveNessCleaning.start()

    # Aliveness thread -Gossip ONLY once on startup
    iAmAliveGossipThread = threading.Thread(target=epidemic_gossip())
    iAmAliveGossipThread.start()

    # User input thread
    # if mode != Mode.planetLab:
    userInputThread = threading.Thread(target=user_input)
    userInputThread.start()
