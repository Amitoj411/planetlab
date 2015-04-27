__author__ = 'Owner'
from SimpleXMLRPCServer import SimpleXMLRPCServer
import NodeList
import settings
import wire
import Mode
import Command
import threading
import Response
import Print
import struct
import AvailabilityAndConsistency

def replicate(key, sender_addr, middle_sender_addr, sixteen_byte_header):
    # global successor_list
    Print.print_("replicating: ", Print.Main, settings.hashedKeyModN, threading.currentThread())

    # Simulate Process replication
    # s1 = s2 = -1
    # s1 = AvailabilityAndConsistency.successor(hash(key) % int(settings.N), 'table')
    # if s1 != int(settings.hashedKeyModN):
    #     s2 = AvailabilityAndConsistency.successor(s1, 'table')
    # print "s1, s2", s1, s2
    #
    # if s1 != -1 and s1 != int(settings.hashedKeyModN):
    #     simulate_forward_rpc_thread1 = threading.Thread(target=replicate_process, args=(s1, key, str(sender_addr), sixteen_byte_header))
    #     simulate_forward_rpc_thread1.start()
    #
    # if s2 != -1 and s2 != int(settings.hashedKeyModN):
    #     simulate_forward_rpc_thread2 = threading.Thread(target=replicate_process, args=(s2, key, str(sender_addr), sixteen_byte_header))
    #     simulate_forward_rpc_thread2.start()
    AvailabilityAndConsistency.update_successor_list()
    for x in settings.successor_list:
        if x != int(settings.hashedKeyModN) and x != -1:
            simulate_forward_rpc_thread1 = threading.Thread(target=replicate_process, args=(x, key, str(sender_addr), middle_sender_addr, sixteen_byte_header))
            simulate_forward_rpc_thread1.start()
            # if response_code != Response.SUCCESS  # Check aliveness and dix the successor list
            # There is no nodes in the network"
        else:
            Print.print_("No successors found. No replicaiton", Print.Main, settings.hashedKeyModN, threading.currentThread())
            # No replications then!


def init():
    global local_rpc_port
    ip_port = NodeList.look_up_node_id(settings.hashedKeyModN, settings.mode)
    local_rpc_port = int(ip_port.split(':')[1]) + 2000


def replicate_process(node_id, key, sender_addr, middle_sender_addr, sixteen_byte_header):
    wireObj = wire.Wire(settings.N, settings.hashedKeyModN, settings.mode, "main")
    value = struct.pack('30s30s16s', sender_addr, middle_sender_addr, sixteen_byte_header)
    wireObj.send_request(Command.REPLICATE_EXECUTE, key, len(value), value, threading.currentThread(), node_id, .1, 0)
    response_code, response_value = wireObj.receive_reply(threading.currentThread(), Command.REPLICATE_EXECUTE)

    # if response_value == Response.SUCCESS:
    #     settings.wireObj.send_reply(sender_addr, "Anykey", Response.SUCCESS, len(""), "", threading.currentThread(), Command.REGISTER, sixteen_byte_header)


def add(key, sender_addr, middle_sender_addr, sixteen_byte_header, command, origin_receiver=True):
    Print.print_("Add start" + " ,component: " + str(key[:5]) + " ,component: " + str(key[5:]), Print.Main, settings.hashedKeyModN, threading.currentThread())
    # print "serving add"
    t = 0
    while t < 1000000:
        t += 1
    # return x + y
    # t1 = len(sixteen_byte_header)
    # print "in add", middle_sender_addr
    if origin_receiver: # remove 16 byte from the cache and send from teh original object
        settings.wireObj.send_reply(sender_addr, "Anykey", Response.SUCCESS, len(str(settings.hashedKeyModN)), str(settings.hashedKeyModN), threading.currentThread(), command, sixteen_byte_header, origin_receiver)
    else:
        wireObj = wire.Wire(settings.N, settings.hashedKeyModN, settings.mode, "main", -2, [-1,-1], middle_sender_addr)  # -2 to enable the SO_REUSEADDR
        wireObj.send_reply(sender_addr, "Anykey", Response.SUCCESS, len(str(settings.hashedKeyModN)), str(settings.hashedKeyModN), threading.currentThread(), command, sixteen_byte_header, origin_receiver)
    Print.print_("Add finish", Print.Main, settings.hashedKeyModN, threading.currentThread())


def subtract(x, y):
    print "serving subtract"
    t = 0
    while t < 1000000:
        t += 1
    return x-y


def multiply(x, y):
    print "serving multiply"
    t = 0
    while t < 1000000:
        t += 1
    return x*y


def divide(x, y):
    print "serving divide"
    t = 0
    while t < 100000:
        t += 1
    return x/y


# def rpc_server():
    # A simple server with simple arithmetic functions
    # server = SimpleXMLRPCServer(("localhost", local_rpc_port))
    # print "RPC server Listening on port ", local_rpc_port, "..."
    # server.register_multicall_functions()
    # server.register_function(add, 'add')
    # server.register_function(subtract, 'subtract')
    # server.register_function(multiply, 'multiply')
    # server.register_function(divide, 'divide')
    # server.serve_forever()