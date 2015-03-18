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
        successor = nodeCommunicationObj.search(key, hashedKeyModN)

    if successor != -2:
        # Print.print_ "The Key Doesn't exist on the network, will return current node"
        if successor != int(hashedKeyModN):  # not the local node
            wireObj.send_request(Command.GET, key, 0, "", threading.currentThread(), successor)
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.GET)  # We are not sending the TA
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
    return response_code, value


def off_load_put(key, value):
    # print("off_load_put {}".format(key))
    if aliveNessTable.get(str(hash(key) % int(N))) >= 0:
        successor = hash(key) % int(N)
    else:
        successor = nodeCommunicationObj.search(key, hashedKeyModN)

    if successor != -2:
        Print.print_("$main: Next alive:" + str(successor), Print.Main, hashedKeyModN)
        if successor != int(hashedKeyModN):  # not the local node
            wireObj.send_request(Command.PUT, key, len(value), value, threading.currentThread(), successor)
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PUT)  # We are sending the TA!
        else:  # local
            response_code = try_to_put(key, value)
    else:  # There is no nodes in the network"
        response_code = try_to_put(key, value)
    return response_code


def off_load_remove(key):
    if aliveNessTable.get(str(hash(key) % int(N))) >= 0:
        successor = hash(key) % int(N)
    else:
        successor = nodeCommunicationObj.search(key, hashedKeyModN)

    if successor != -2:
        Print.print_("$main: Next alive:" + str(successor), Print.Main, hashedKeyModN)
        if successor != int(hashedKeyModN):  # not the local node
            wireObj.send_request(Command.REMOVE, key, 0, "", threading.currentThread(), successor)
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.REMOVE)  # We are not sending the TA
        else:
            response_code = try_to_remove(key)
    else:
        response_code = try_to_remove(key)
        if response_code != Response.SUCCESS:
            response_code = Response.NoExternalAliveNodes
    return response_code


# class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
#         pass
#
#
# class ThreadedUDPRequestHandler(SocketServer.BaseRequestHandler):
#     def handle(self):
#         # data = self.request[0].strip()
#         # socket = self.request[1]
#         # print("{} wrote: ".format(self.client_address[0]))
#         # print(data)
#         # socket.sendto(data.upper(), self.client_address)
#         cur_thread = threading.currentThread()

# while True:
#             command, key, value_length, value, sender_addr = wireObj.receive_request(hashedKeyModN, self, cur_thread)

def receive_request():
        while True:
            cur_thread = threading.currentThread()
            command, key, value_length, value, sender_addr = wireObj.receive_request(hashedKeyModN, cur_thread)
            if command == Command.PUT:
                response = off_load_put(key, value)
                wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.PUT)

            elif command == Command.GET:
                response, value = off_load_get(key)
                value_to_send = value
                wireObj.send_reply(sender_addr, key, response, len(value_to_send), value_to_send, cur_thread, Command.GET)

            elif command == Command.REMOVE:
                response = off_load_remove(key)
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
                    if hash(k) % int(N) == join_id \
                            or (hash(k) % int(N) < join_id and hash(k) % int(N) < hashedKeyModN) \
                            or (hash(k) % int(N) > join_id):  # ensure joinID is the ID of the predecessor or the upper
                            # space between the joined node and the received node

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
            elif command == Command.ALIVE:
                wireObj.send_reply(sender_addr, key, Response.SUCCESS, 0, "", cur_thread, Command.ALIVE)
                # Send msg Epidemicly
                if key != hashedKeyModN:
                    increament(key)
                    epidemic(int(key))

            else:
                response = Response.UNRECOGNIZED
                wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.PUT)  # no unrecog command


def increament(key):
    if aliveNessTable.get(key) is None:
        aliveNessTable.put(key, 0)
    else:
        if int(aliveNessTable.get(key)) + 1 > 3:  # max 3
            aliveNessTable.put(key, 3)
        else:
            # print "int(aliveNessTable.get(key)) + 1:::::"+int(aliveNessTable.get(key)) + 1
            aliveNessTable.put(key, int(aliveNessTable.get(key)) + 1)


def epidemic(key):
    counter = 0
    while counter < int(math.log(int(N), 2)):
        # print "Iteration: " + str(counter)
        randomNode = otherNode()
        if key != randomNode:
            wireObj.send_request(Command.ALIVE, str(key), 0, "", threading.currentThread(), randomNode, retrials=0)
            response_code, value = wireObj.receive_reply(threading.currentThread(), Command.ALIVE)  # We are not sending the TA
            if response_code == Response.SUCCESS:
                increament(str(randomNode))
        counter += 1


def otherNode():
    tmp = random.randint(0, int(N) - 1)
    if tmp == int(hashedKeyModN):
        return otherNode()
    else:
        return int(tmp)


def iAmAlive():
    while True:
        # print "iAmAlive"
        # Send Alive(push) msg every 5s to a random node
        randomNode = otherNode()
        wireObj.send_request(Command.ALIVE, hashedKeyModN, 0, "", threading.currentThread(), randomNode, retrials=0)
        response_code, value = wireObj.receive_reply(threading.currentThread(), Command.ALIVE)  # We are not sending the TA
        if response_code == Response.SUCCESS:
            if not aliveNessTable.get(str(randomNode)):
                aliveNessTable.put(str(randomNode), 0)  # initialization
            else:
                if aliveNessTable.get(str(randomNode)) + 1 > 3:  # max 3
                    aliveNessTable.put(str(randomNode), 3)
                else:
                    aliveNessTable.put(str(randomNode), aliveNessTable.get(str(randomNode)) + 1)
        time.sleep(2)


def aliveNessCleaning():
    while True:
        time.sleep(7)
        # if len(aliveNessTable.hashTable.) > 0:
        for k in aliveNessTable.hashTable:
            if aliveNessTable.get(k) - 2 < -1:  # min =-1
                aliveNessTable.put(k, -1)
                # print "cleanin1"
            else:
                aliveNessTable.put(k, aliveNessTable.get(k) - 2)


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

    receiveThread = threading.Thread(target=receive_request)
    receiveThread.start()

    ip_port = NodeList.look_up_node_id(hashedKeyModN, mode)
    # MULTI-THREADED SERVER
    # if mode == Mode.planetLab:
    #     udp_server = ThreadedUDPServer((NodeList.get_ip_address(ip_port.split(':')[0]),
    #                                     int(ip_port.split(':')[1])), ThreadedUDPRequestHandler)
    # else:
    #     udp_server = ThreadedUDPServer((ip_port.split(':')[0], int(ip_port.split(':')[1])), ThreadedUDPRequestHandler)
    # udp_thread = threading.Thread(target=udp_server.serve_forever)
    # udp_thread.start()

    nodeCommunicationObj.join(int(hashedKeyModN)) # call joining procedure

    time.sleep(1.5)

    # Aliveness thread
    iAmAliveThread = threading.Thread(target=iAmAlive)
    iAmAliveThread.start()
    # Aliveness-cleaning thread
    aliveNessCleaning = threading.Thread(target=aliveNessCleaning)
    aliveNessCleaning.start()

    # User input thread
    if mode != Mode.planetLab:
        userInputThread = threading.Thread(target=user_input)
        userInputThread.start()
