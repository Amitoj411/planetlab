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
import math
import Response
import settings
import MembershipProtocol
import Replication
import ProcessManagement
import struct
import  partitioning


def off_load_get_thread(key, sender_addr, sixteen_byte_header):
    # if item is replicated it might be stored locally
    response_local, value_local = try_to_get(key)
    if response_local == Response.SUCCESS:
        settings.wireObj.send_reply(sender_addr, key, response_local, len(value_local), value_local, threading.currentThread(), Command.GET, sixteen_byte_header)
    else:
        response, value = off_load_get(key)
        value_to_send = value
        settings.wireObj.send_reply(sender_addr, key, response, len(value_to_send), value_to_send, threading.currentThread(), Command.GET, sixteen_byte_header)


def off_load_get(key):
    if settings.aliveNessTable.isAlive(str(hash(key) % int(N))):
        successor_ = hash(key) % int(N)
    else:
        successor_ = AvailabilityAndConsistency.search(key, "table")
    # print "successor_: " + str(successor_) + ",str(settings.aliveNessTable.get(str(hash(key) % int(N)))):" + str(settings.aliveNessTable.get(str(hash(key) % int(N))))
    if successor_ != int(settings.hashedKeyModN):  # not the local node
        settings.wireObj.send_request(Command.GET_HINTED, key, 0, "", threading.currentThread(), successor_)
        response_code, value = settings.wireObj.receive_reply(threading.currentThread(), Command.GET)

        if response_code != Response.SUCCESS and response_code != Response.NONEXISTENTKEY:  # NOREPLY
            # PING it, if dead. Declare dead and call recursively
            # settings.wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), successor_)
            # response_code_, value_ = settings.wireObj.receive_reply(threading.currentThread(), Command.PING)
            # if response_code_ != Response.SUCCESS:  # Declare dead
                # print "recursive find" + ", successor_:" + str(successor_) + ", settings.aliveNessTable.get(successor_)" + \
                #     str(settings.aliveNessTable.get(successor_))
                # settings.aliveNessTable.remove(str(successor_))  # May be penalize in the negative to solve teh later msgs on the way
            settings.aliveNessTable.put(str(successor_), 0)
            response_code, value = off_load_get(key)
            # else:
            #     response_code, value = off_load_get(key)
        else:
            Print.print_("Value:" + str(value), Print.Main, settings.hashedKeyModN)

    else:  # the local node
        response_code, value = try_to_get(key)

    return response_code, value


def off_load_put_thread(key, value, sender_addr, sixteen_byte_header):
    # print threading.currentThread().getName(), 'Starting'
    # non-blocking
    settings.wireObj.send_reply(sender_addr, key, Response.SUCCESS, 0, "", threading.currentThread(), Command.PUT, sixteen_byte_header)
    # print "reply is sent now replicating"
    response = off_load_put(key, value)
    # print threading.currentThread().getName(), 'Exiting'


def off_load_put(key, value):
    if settings.aliveNessTable.isAlive(str(hash(key) % int(N))):
        successor_ = hash(key) % int(N)
    else:
        successor_ = AvailabilityAndConsistency.search(key, "table")

    # if successor_ != -2:
    if successor_ != int(settings.hashedKeyModN):  # not the local node
        # print "remote"

        settings.wireObj.send_request(Command.PUT_HINTED, key, len(value), value, threading.currentThread(), successor_)
        response_code, value_ = settings.wireObj.receive_reply(threading.currentThread(), Command.PUT)

        # SUDDEN DEATH OR SUDDEN JOIN
        if response_code != Response.SUCCESS:  # probably dead but not yet propagated, Workaround procedure
            # PING it, if dead. Declare dead and call recursively
            # settings.wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), successor_)
            # response_code_, value_ = settings.wireObj.receive_reply(threading.currentThread(), Command.PING)
            # if response_code_ != Response.SUCCESS:  # Declare dead
            print "recursive find"
                # settings.aliveNessTable.remove(successor_)
            settings.aliveNessTable.put(str(successor_), 0)
            response_code = off_load_put(key, value)
            # else:
            #     response_code = off_load_put(key, value)

    else:  # local
        # print "local"
        response_code = try_to_put(key, value)
        replicate_put_thread = threading.Thread(target=Replication.replicate, args=(Command.PUT, key, value))
        replicate_put_thread.start()
    return response_code


def off_load_remove_thread(key, sender_addr, sixteen_byte_header):
    # non blocking
    settings.wireObj.send_reply(sender_addr, key, Response.SUCCESS, 0, "", threading.currentThread(), Command.REMOVE, sixteen_byte_header)
    response = off_load_remove(key)



def off_load_remove(key):
    if settings.aliveNessTable.isAlive(str(hash(key) % int(N))):
        successor_ = hash(key) % int(N)
    else:
        successor_ = AvailabilityAndConsistency.search(key, "table")

    if successor_ != int(settings.hashedKeyModN):  # not the local node
        settings.wireObj.send_request(Command.REMOVE_HINTED, key, 0, "", threading.currentThread(), successor_)
        response_code, value = settings.wireObj.receive_reply(threading.currentThread(), Command.REMOVE)

        # SUDDEN DEATH probably dead but not yet propagated, Workaround procedure
        if response_code != Response.SUCCESS and response_code != Response.NONEXISTENTKEY:
                # PING it, if dead. Declare dead and call recursively
                # settings.wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), successor_)
                # response_code_, value_ = settings.wireObj.receive_reply(threading.currentThread(), Command.PING)
                # if response_code_ != Response.SUCCESS:  # Declare dead
                    # settings.aliveNessTable.remove(successor_)
                settings.aliveNessTable.put(str(successor_), 0)
                response_code = off_load_remove(key)
                # else:
                #     response_code = off_load_remove(key)

    else:  # local
        response_code = try_to_remove(key)
        replicate_remove_thread = threading.Thread(target=Replication.replicate, args=(Command.REMOVE, key))
        replicate_remove_thread.start()
    return response_code


def off_load_process(key, sender_addr, middle_sender_addr, sixteen_byte_header):  # TODO make it as GET, PUT, REMOVE
    if settings.aliveNessTable.isAlive(str(hash(key) % int(N))):
        successor_ = hash(key) % int(N)
    else:
        successor_ = AvailabilityAndConsistency.search(key, "table")
    # print sender_addr
    if successor_ != int(settings.hashedKeyModN):  # not the local node
        value = struct.pack('30s30s16s', str(sender_addr), str(middle_sender_addr), sixteen_byte_header)
        t1=len(sixteen_byte_header)
        settings.wireObj.send_request(Command.EXECUTE_HINTED, key, len(value), value, threading.currentThread(), successor_)
        response_code, response_value = settings.wireObj.receive_reply(threading.currentThread(), Command.EXECUTE_HINTED)
    else:  # local
        simulate_thread = threading.Thread(target=ProcessManagement.add, args=(key, sender_addr, middle_sender_addr, sixteen_byte_header, Command.EXECUTE_HINTED, True))
        simulate_thread.start()

        replicate_process_thread = threading.Thread(target=ProcessManagement.replicate, args=(key, sender_addr, middle_sender_addr, sixteen_byte_header))
        replicate_process_thread.start()



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
        #             command, key, value_length, value, sender_addr = settings.wireObj.receive_request(settings.hashedKeyModN, cur_thread, self)
        receive_request(self)


def replicate_get(key, sender_addr, sixteen_byte_header):
    # global successor_list
    Print.print_("replicating get: ", Print.Main, settings.hashedKeyModN, threading.currentThread())

    AvailabilityAndConsistency.update_successor_list()
    for x in settings.successor_list:
        if x != int(settings.hashedKeyModN) and x != -1:
            simulate_forward_rpc_thread1 = threading.Thread(target=replicate_get_process, args=(x, key, str(sender_addr), sixteen_byte_header))
            simulate_forward_rpc_thread1.start()
            # if response_code != Response.SUCCESS  # Check aliveness and dix the successor list
            # There is no nodes in the network"
        else:
            Print.print_("No successors found. No replicaiton", Print.Main, settings.hashedKeyModN, threading.currentThread())
            # No replications then!

def replicate_get_process(node_id, key, sender_addr, sixteen_byte_header):
    wireObj = wire.Wire(settings.N, settings.hashedKeyModN, settings.mode, "main")
    value = struct.pack('30s16p', sender_addr, sixteen_byte_header)
    wireObj.send_request(Command.REPLICATE_GET, key, len(value), value, threading.currentThread(), node_id, .2, 0)
    response_code, response_value = wireObj.receive_reply(threading.currentThread(), Command.REPLICATE_EXECUTE)


def receive_request(handler=""):
    while True:
        cur_thread = threading.currentThread()
        Print.print_("Waiting for a request", Print.Main, settings.hashedKeyModN, cur_thread)
        command, key, value_length, value, sender_addr, sixteen_byte_header = settings.wireObj.receive_request(settings.hashedKeyModN, cur_thread, handler)
        if command == Command.PUT:
            # If you do the next, all msgs received but not, all replies sent back, but not all received (receiver problem ?)
            offload_put_thread = threading.Thread(target=off_load_put_thread, args=(key, value, sender_addr, sixteen_byte_header))
            offload_put_thread.start()

            # If you do the next, some msgs will be not receieved at all!
            # settings.wireObj.send_reply(sender_addr, key, Response.SUCCESS, 0, "", cur_thread, Command.PUT)
            # response = off_load_put(key, value)

        elif command == Command.PUT_HINTED:
            response = try_to_put(key, value)
            settings.wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.PUT_HINTED, sixteen_byte_header)
            replicate_thread = threading.Thread(target=Replication.replicate, args=(Command.PUT, key, value))
            replicate_thread.start()

        elif command == Command.GET:
            offload_get_thread = threading.Thread(target=off_load_get_thread, args=(key, sender_addr, sixteen_byte_header))
            offload_get_thread.start()
            # response, value = off_load_get(key)
            # value_to_send = value
            # settings.wireObj.send_reply(sender_addr, key, response, len(value_to_send), value_to_send, cur_thread, Command.GET)

            # REPLICATE GET Simulation
            # replicate_process_thread = threading.Thread(target=replicate_get, args=(key, sender_addr, sixteen_byte_header))
            # replicate_process_thread.start()

        elif command == Command.GET_HINTED:
            response, value_to_send = try_to_get(key)
            settings.wireObj.send_reply(sender_addr, key, response, len(value_to_send), value_to_send, cur_thread, Command.GET, sixteen_byte_header)

            # REPLICATE GET Simulation
            # replicate_process_thread = threading.Thread(target=replicate_get, args=(key, sender_addr, sixteen_byte_header))
            # replicate_process_thread.start()

        elif command == Command.REPLICATE_GET:
            settings.wireObj.send_reply(sender_addr, "Anykey", Response.SUCCESS, len(""), "", cur_thread, Command.REPLICATE_GET, sixteen_byte_header)
            sender_addr_, sixteen_byte_header_ = struct.unpack('30s16p', value)
            response, value_to_send = try_to_get(key)
            # settings.wireObj_replicate.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REPLICATE_GET, sixteen_byte_header)
            print sender_addr_
            print eval(sender_addr_)
            settings.wireObj.send_reply(eval(sender_addr_)
                                        , key, response, len(value_to_send), value_to_send, threading.currentThread(), Command.REPLICATE_GET, sixteen_byte_header_, False)

        elif command == Command.REMOVE:
            offload_remove_thread = threading.Thread(target=off_load_remove_thread, args=(key, sender_addr, sixteen_byte_header))
            offload_remove_thread.start()
            # response = off_load_remove(key)
            # settings.wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REMOVE)

        elif command == Command.REMOVE_HINTED:
            response = try_to_remove(key)
            settings.wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.REMOVE, sixteen_byte_header)

            replicate_thread = threading.Thread(target=Replication.replicate, args=(Command.REMOVE, key))
            replicate_thread.start()

        elif command == Command.SHUTDOWN:
            response = Response.SUCCESS
            settings.wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.SHUTDOWN, sixteen_byte_header)
            os._exit(10)

        elif command == Command.PING:
            response = Response.SUCCESS
            value = "Alive!"
            settings.wireObj.send_reply(sender_addr, key, response, len(value), value, cur_thread, Command.PING, sixteen_byte_header)

        elif command == Command.JOIN_SUCCESSOR:
            join_id = int(value)
            settings.wireObj.send_reply(sender_addr, "", Response.SUCCESS, 0, "", cur_thread, Command.JOIN_SUCCESSOR, sixteen_byte_header)
            # keys_to_be_deleted = []
            for k in settings.kvTable.hashTable:
                distance = int(math.fabs(int(settings.hashedKeyModN) - join_id))
                # if distance == 1 and (hash(k) % int(N) > int(settings.hashedKeyModN) or hash(k) % int(N) == join_id) or \
                #         (distance > 1 and hash(k) % int(N) == join_id) or \
                #                 distance_node_to_key(join_id, k) <= distance_node_to_key(int(settings.hashedKeyModN), k):
                # is_join_have_local_as_successor = AvailabilityAndConsistency.if_join_have_local_as_successor(join_id)
                if hash(k) % int(N) == join_id:  # and is_join_have_local_as_successor:
                    key_value = settings.kvTable.hashTable[k]
                    settings.wireObj_replicate.send_request(Command.REPLICATE_PUT, k, len(key_value), key_value,
                                         threading.currentThread(), join_id)
                    response_code, value = settings.wireObj_replicate.receive_reply(threading.currentThread(), Command.PUT)
                    # if response_code == Response.SUCCESS:
                    #     keys_to_be_deleted.append(k)
                    # else:
                    #     Print.print_("The joined node is dead for this key" + ", response: " +
                    #                  Response.print_response(response_code), Print.Main, settings.hashedKeyModN)
            # for k in keys_to_be_deleted:
            #     settings.kvTable.remove(k)

        elif command == Command.JOIN_PREDECESSOR:
            join_id = int(value)
            settings.wireObj.send_reply(sender_addr, "", Response.SUCCESS, 0, "", cur_thread, Command.JOIN_SUCCESSOR, sixteen_byte_header)

            for k in settings.kvTable.hashTable:
                # is_local_have_join_as_successor = AvailabilityAndConsistency.if_local_have_join_as_successor(join_id)
                if hash(k) % int(N) == int(settings.hashedKeyModN):  # and is_local_have_join_as_successor:
                    key_value = settings.kvTable.hashTable[k]
                    settings.wireObj_replicate.send_request(Command.REPLICATE_PUT, k, len(key_value), key_value,
                                         threading.currentThread(), join_id)
                    response_code, value = settings.wireObj_replicate.receive_reply(threading.currentThread(), Command.PUT)

        elif command == Command.EXECUTE:
            game_id = key[:5]
            # component_name = value
            component_name = key[5:]

            # Load Balancing
            # forward_node = hash(client_id + game_id) % int(N)
            forward_node = hash(game_id + component_name) % int(N)
            print "forward_node for ", game_id + component_name, ":", forward_node


            ip_port = NodeList.look_up_node_id(settings.hashedKeyModN, mode)
            middle_sender_addr = ip_port.split(':')[0]
            # print "in EXECUTE", middle_sender_addr
            if forward_node == int(settings.hashedKeyModN):
                # ip_port_ = NodeList.look_up_node_id(settings.hashedKeyModN, mode)

                # EXECUTE Simulation
                simulate_thread = threading.Thread(target=ProcessManagement.add, args=(key, sender_addr, middle_sender_addr, sixteen_byte_header, command, True))
                simulate_thread.start()

                # REPLICATE EXECUTE Simulation
                replicate_process_thread = threading.Thread(target=ProcessManagement.replicate, args=(key, sender_addr, middle_sender_addr, sixteen_byte_header))
                replicate_process_thread.start()



            else:  # other node
                # Send hinted-off
                offload_process_thread = threading.Thread(target=off_load_process, args=(key, sender_addr, middle_sender_addr
                                                                                         , sixteen_byte_header))
                offload_process_thread.start()





        elif command == Command.REPLICATE_EXECUTE:
                settings.wireObj.send_reply(sender_addr, "Anykey", Response.SUCCESS, len(""), "", cur_thread, Command.REPLICATE_EXECUTE, sixteen_byte_header)

                sender_addr_, middle_sender_addr, sixteen_byte_header_ = struct.unpack('30s30s16s', value)
                simulate_thread = threading.Thread(target=ProcessManagement.add, args=(key, eval(sender_addr_.strip(' \t\r\n\0')), middle_sender_addr.strip(' \t\r\n\0'),  sixteen_byte_header_, command, False))  # False == not the original receiver
                simulate_thread.start()


        elif command == Command.EXECUTE_HINTED:
                settings.wireObj.send_reply(sender_addr, "Anykey", Response.SUCCESS, len(""), "", cur_thread, Command.EXECUTE_HINTED, sixteen_byte_header)

                sender_addr_, middle_sender_addr, sixteen_byte_header_ = struct.unpack('30s30s16s', value)
                # t1 = len(sixteen_byte_header_)
                # print t1
                # print "sender_addr_, sixteen_byte_header_", sender_addr_, sixteen_byte_header_
                print middle_sender_addr
                # eval(sender_addr_.strip(' \t\r\n\0'))
                simulate_thread = threading.Thread(target=ProcessManagement.add, args=(key, eval(sender_addr_.strip(' \t\r\n\0')),
                                                                                        middle_sender_addr.strip(' \t\r\n\0'),
                                                                                        sixteen_byte_header_,
                                                                                        command, False))
                simulate_thread.start()

                # REPLICATE EXECUTE Simulation
                replicate_process_thread = threading.Thread(target=ProcessManagement.replicate, args=(key, sender_addr_, middle_sender_addr.strip(' \t\r\n\0'), sixteen_byte_header_))
                replicate_process_thread.start()


        else:
            response = Response.UNRECOGNIZED
            settings.wireObj.send_reply(sender_addr, key, response, 0, "", cur_thread, Command.PUT, sixteen_byte_header)


def try_to_get(key):
    value_to_send = ("", )
    try:
        value = settings.kvTable.get(key)
        Print.print_("KV[" + str(key) + "]=" + str(settings.kvTable.get(key)), Print.Main, settings.hashedKeyModN, threading.currentThread())
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
        value = settings.kvTable.remove(key)
        if value == "does no exist":
            raise KeyError
        else:
            Print.print_("Removing KV[" + str(key) + "]=" + value, Print.Main, settings.hashedKeyModN)
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
        # if settings.kvTable.size() > 64000000:
        #     raise Exceptions.OutOfSpaceException()
        # else:
        settings.kvTable.put(key, value)
        Print.print_(" KV[" + str(key) + "]=" + value, Print.Main, settings.hashedKeyModN, threading.currentThread())
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
        print "\nmain$ [node_id:" + str(settings.hashedKeyModN) + "] Please Enter one of the following:" + "\n" +\
              "     1- Print the local Key-value store:            5- Search for a key:" + "\n" + \
              "     2- Get a value for a key (KV[key]):            6- Shutdown a node by (key/node_id):" + "\n" + \
              "     3- Put a value for a key (KV[key]=value):      7- Ping a node by (key/node_id):" + "\n" + \
              "     4- Remove a key from KV):                      8- Turn debugging msgs ON/OFF" + "\n" + \
              "     9- Print ServerCache                           10- Print Alive nodes" + "\n" +\
              "     11- print successor table                      Other- Exit"

        nb = raw_input('>')
        if nb == "1":
            settings.kvTable._print()
        elif nb == "2":  # GET
            key = raw_input('Main$ Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(settings.hashedKeyModN):
                response_code, value = try_to_get(key)
            else:  # Not local
                response_code, value = off_load_get(key)
            Print.print_("Response:" + Response.print_response(response_code), Print.Main, settings.hashedKeyModN)

        elif nb == "3":  # PUT
            key = raw_input('Main$ Please enter the key>')
            value = raw_input('Main$ Please enter the value>')
            if hash(key) % int(N) == int(settings.hashedKeyModN):
                response_code = try_to_put(key, value)

                replicate_thread = threading.Thread(target=Replication.replicate, args=(Command.PUT, key, value))
                replicate_thread.start()
            else:
                response_code = off_load_put(key, value)
            Print.print_("Response:" + Response.print_response(response_code), Print.Main, settings.hashedKeyModN)

        elif nb == "4":  # remove
            key = raw_input('Main$ Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(settings.hashedKeyModN):
                response_code = try_to_remove(key)

                replicate_thread = threading.Thread(target=Replication.replicate, args=(Command.REMOVE, key))
                replicate_thread.start()
            else:
                response_code = off_load_remove(key)
            Print.print_("response:" + Response.print_response(response_code), Print.Main, settings.hashedKeyModN)
        elif nb == "5":   # search
            key = raw_input('Main$ Please enter the key>')
            output = AvailabilityAndConsistency.search(key, "table")
            Print.print_("The Result is: " + str(output), Print.Main, settings.hashedKeyModN)
        elif nb == "6":   # Shutdown
            option = raw_input('Main$ Shutdown by key (y/n)?>')
            if option == "y" or option == "yes":
                key = raw_input('Main$ Please enter the key>')
                # Check if the key is stored locally else send a request
                if hash(key) % int(N) == int(settings.hashedKeyModN):
                    os._exit(10)
                    response_code = Response.SUCCESS
                else:
                    settings.wireObj.send_request(Command.SHUTDOWN, key, 0, "", threading.currentThread(), -1)
                    response_code, value = settings.wireObj.receive_reply(threading.currentThread(), Command.SHUTDOWN)  
                Print.print_("response:" + Response.print_response(response_code),
                             Print.Main, settings.hashedKeyModN)
            else:
                node_id = raw_input('Main$ Please enter the node_id>')
                if int(node_id) == int(settings.hashedKeyModN):
                    os._exit(10)
                    response_code = Response.SUCCESS
                else:
                    settings.wireObj.send_request(Command.SHUTDOWN, "AnyKey", 0, "", threading.currentThread(), node_id)
                    response_code, value = settings.wireObj.receive_reply(threading.currentThread(), Command.SHUTDOWN)  
                Print.print_("response:" + Response.print_response(response_code), Print.Main, settings.hashedKeyModN)
        elif nb == "7":   # Ping
            option = raw_input('Main$ Ping by key (y/n)?>')
            if option == "y" or option == "yes":
                key = raw_input('Main$ Please enter the key>')
                # Check if the key is stored locally else send a request
                if hash(key) % int(N) == int(settings.hashedKeyModN):
                    value = ("Alive!",)
                    response_code = Response.SUCCESS
                else:
                    settings.wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), -1)
                    response_code, value = settings.wireObj.receive_reply(threading.currentThread(), Command.PING)  
                Print.print_("response:" + Response.print_response(response_code), Print.Main, settings.hashedKeyModN)
                if response_code == Response.SUCCESS: Print.print_("Reply:" + str(value[0]), Print.Main, settings.hashedKeyModN)
            else:
                node_id = raw_input('Main$ Please enter the node_id>')
                if int(node_id) == int(settings.hashedKeyModN):
                    value = ("Alive!",)
                    response_code = Response.SUCCESS
                else:
                    settings.wireObj.send_request(Command.PING, "AnyKey", 0, "", threading.currentThread(), node_id)
                    response_code, value = settings.wireObj.receive_reply(threading.currentThread(), Command.PING)  
                Print.print_("response:" + Response.print_response(response_code), Print.Main, settings.hashedKeyModN)
                if response_code == Response.SUCCESS: Print.print_("Reply:" + str(value[0]), Print.Main, settings.hashedKeyModN)
        elif nb == "8":   # Toggle debugging
            if Print.debug:
                Print.debug = False
            else:
                Print.debug = True
        elif nb == "9":   # Print ServerCache
            settings.wireObj.RequestReplyServer_obj.cache._print()
        elif nb == "10":
            settings.aliveNessTable._print()
        elif nb == "11":
            for x in settings.successor_list:
                print x

        else:
            # sys.exit("Exit normally.")
            os._exit(10)


if __name__ == "__main__":
    global hashedKeyModN, N, mode
    opts, args = getopt.getopt(sys.argv, "", [""])
    N = args[1]
    # mode = ""
    # settings.hashedKeyModN = ""

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
    settings.init(N, hashedKeyModN, mode)

    # settings.wireObj = wire.Wire(int(N), settings.hashedKeyModN, mode, "main", settings.successor_list)

    # nodeCommunicationObj = AvailabilityAndConsistency.NodeCommunication(int(N), mode, settings.hashedKeyModN)

    # Replication.init()
    # MembershipProtocol.init()


    multiThreadUDPServer = False
    if not multiThreadUDPServer:  # Single threaded UDP server
        receiveThread = threading.Thread(target=receive_request)
        receiveThread.start()

        receive_request_push_alive_only_Thread = threading.Thread(target=MembershipProtocol.receive_request_push_alive_only)
        receive_request_push_alive_only_Thread.start()

        receive_request_replicate_only_Thread = threading.Thread(target=Replication.receive_request_replicate_only)
        receive_request_replicate_only_Thread.start()

    else:  # multiThreaded
        ip_port = NodeList.look_up_node_id(settings.hashedKeyModN, mode)
        # MULTI-THREADED SERVER
        if mode == Mode.planetLab:
            udp_server = ThreadedUDPServer((NodeList.get_ip_address(ip_port.split(':')[0]),
                                            int(ip_port.split(':')[1])), ThreadedUDPRequestHandler)
        else:
            udp_server = ThreadedUDPServer((ip_port.split(':')[0], int(ip_port.split(':')[1])), ThreadedUDPRequestHandler)
        udp_thread = threading.Thread(target=udp_server.serve_forever)
        udp_thread.start()

    # nodeCommunicationObj.join(int(settings.hashedKeyModN), settings.aliveNessTable)  # call joining procedure
    # nodeCommunicationObj.join_successor()  # call joining procedure

    #  Aliveness thread anti-antropy will run periodically
    # iAmAliveAntriAntropyThread = threading.Thread(target=MembershipProtocol.i_am_alive_antri_antropy)
    # iAmAliveAntriAntropyThread.start()
    #
    # i_am_alive_small_network = threading.Thread(target=MembershipProtocol.i_am_alive_small_network)
    # i_am_alive_small_network.start()

    # #  Aliveness-cleaning thread
    # aliveNessCleaning = threading.Thread(target=MembershipProtocol.decrement_soft_state)
    # aliveNessCleaning.start()

    # Aliveness thread -Gossip ONLY once on startup
    # iAmAliveGossipThread = threading.Thread(target=MembershipProtocol.epidemic_gossip)
    # iAmAliveGossipThread.start()

    #
    check_random_nodesThread = threading.Thread(target=MembershipProtocol.check_random_nodes)
    check_random_nodesThread.start()

    epidemically_send_local_route_stateThread = threading.Thread(target=MembershipProtocol.epidemically_send_local_route)
    epidemically_send_local_route_stateThread.start()

    # clean_route_stateThread = threading.Thread(target=MembershipProtocol.clean_route_state)
    # clean_route_stateThread.start()

    time.sleep(1)

    # User input thread
    if mode != Mode.planetLab:
        userInputThread = threading.Thread(target=user_input)
        userInputThread.start()

    ProcessManagement.init()
    # rpc_serverThread = threading.Thread(target=ProcessManagement.rpc_server)
    # rpc_serverThread.start()


    time.sleep(2)
    AvailabilityAndConsistency.join_successor()
    time.sleep(1.5)
    AvailabilityAndConsistency.join_predecessor()  # call joining procedure


    clean_up_replicated_keys_thread = threading.Thread(target=Replication.clean_up_replicated_keys)
    clean_up_replicated_keys_thread.start()
