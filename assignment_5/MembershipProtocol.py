__author__ = 'Owner'
import settings
import random
import threading
import Command
import Response
import wire
import time
import math

contaminated = False

# def init():
#     global settings.wireObj_push_alive
#     settings.wireObj_push_alive = wire.Wire(int(settings.N), settings.hashedKeyModN, settings.mode, "epidemic", settings.successor_list)

def receive_request_push_alive_only(handler=""):
    global contaminated

    while True:
        cur_thread = threading.currentThread()
        command, key, value_length, value, sender_addr, sixteen_byte_header = settings.wireObj_push_alive.receive_request(settings.hashedKeyModN, cur_thread, handler)
        if command == Command.PUSH:
            value_piggybacking = settings.aliveNessTable.get_list_of_alive_keys()
            value_piggybacking = ",".join(value_piggybacking)
            settings.wireObj_push_alive.send_reply(sender_addr, key, Response.SUCCESS, len(value_piggybacking), value_piggybacking, cur_thread, Command.PUSH, sixteen_byte_header)
            # Send msg Epidemicly; anti-antrpoy
            if int(key) != int(settings.hashedKeyModN):
                increment_soft_state(key)
                list_of_alive_nodes = value.split(',')
                update_incoming(list_of_alive_nodes)

                if not contaminated:
                    epidemic_anti_antropy(key)
                    contaminated = True

        elif command == Command.ALIVE:
            # Biggy back reply
            value_piggybacking = settings.aliveNessTable.get_list_of_alive_keys()
            value_piggybacking = ",".join(value_piggybacking)
            settings.wireObj_push_alive.send_reply(sender_addr, key, Response.SUCCESS, len(value_piggybacking), value_piggybacking, cur_thread, Command.ALIVE, sixteen_byte_header)

            list_of_alive_nodes = value.split(',')
            update_incoming(list_of_alive_nodes)
            if int(key) != int(settings.hashedKeyModN):
                increment_soft_state(key)

            if not contaminated:
                epidemic_anti_antropy(key)
                contaminated = True


# Increment all the incoming updates.. PUSH
def update_incoming(list_of_alive_nodes):
    global contaminated
    for x in list_of_alive_nodes:  # Increment the status of all alive nodes
        if x is not None and x is not "":
            try:
                k, count = x.split(':')
            except:
                print "x >>:", x

                raise
            if int(k) != int(settings.hashedKeyModN) and k != "":
                if settings.aliveNessTable.get(k) is not None:
                    if int(count) > int(settings.aliveNessTable.get(k)):
                        increment_soft_state(k)
                        # print "BONUS!: " + str(k),
                else:  # if does not exist locally, increment!
                    # print "NEW LIFE!!: " + str(k)
                    increment_soft_state(k)


# Increment the soft state
def increment_soft_state(key):
    if settings.aliveNessTable.get(key) is None:
        settings.aliveNessTable.put(key, 0)
    else:
        if int(settings.aliveNessTable.get(key)) + 1 > 3:  # max 3
            settings.aliveNessTable.put(key, 3)
        else:
            settings.aliveNessTable.put(key, int(settings.aliveNessTable.get(key)) + 1)


def epidemic_gossip():
    sum_counter = 0 # Total Alive msgs
    print "epidemic gossip"
    while True:  # Send to log(settings.N) nodes
        print ".",
        counter = 0
        while counter < int(math.log(int(settings.N), 2)):
            randomNode = other_node()
            # print "Iteration: " + str(counter) + "randomNode" + str(randomNode)
            value = settings.aliveNessTable.get_list_of_alive_keys()
            value = ",".join(value)
            settings.wireObj_push_alive.send_request(Command.ALIVE, str(settings.hashedKeyModN), len(value), value,
                                 threading.currentThread(), randomNode, retrials=2)
            response_code, value_biggy = settings.wireObj_push_alive.receive_reply(threading.currentThread(), Command.ALIVE)
            if response_code == Response.SUCCESS:
                increment_soft_state(str(randomNode))
                value_biggy = value_biggy.split(',')
                update_incoming(value_biggy)
            counter += 1
            time.sleep(1)  # not to overwhelm 1 node in small rings
        sum_counter += counter
        # Stop with probability 1/k
        if int(settings.N) >= 10:
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
    while counter < int(math.log(int(settings.N), 2)):
        # print "Iteration: " + str(counter)
        random_node = other_node(key)
        if key != random_node:
            value = settings.aliveNessTable.get_list_of_alive_keys()
            value = ",".join(value)
            settings.wireObj_push_alive.send_request(Command.PUSH, str(key), len(value), value,
                                 threading.currentThread(), random_node, retrials=2)
            response_code, value_biggy = settings.wireObj_push_alive.receive_reply(threading.currentThread(), Command.PUSH)
            if response_code == Response.SUCCESS:
                increment_soft_state(str(random_node))
                value_biggy = value_biggy.split(',')
                update_incoming(value_biggy)
        counter += 1
        time.sleep(.2)  # not to overwhelm 1 node in small rings


def other_node(sender="-1"):  # exclude sender as well
    tmp = random.randint(0, int(settings.N) - 1)
    # print sender
    if tmp == int(settings.hashedKeyModN) or tmp == int(sender):
        return other_node()
    else:
        return int(tmp)


def i_am_alive_antri_antropy():
    global contaminated
    while True:
        if int(settings.N) > 10:
            r = random.randint(2, 3)  # periodically
        else:
            r = random.randint(2, 4)  # periodically
        time.sleep(r)
        random_node = other_node()
        value = settings.aliveNessTable.get_list_of_alive_keys()
        value = ",".join(value)
        settings.wireObj_push_alive.send_request(Command.PUSH, str(settings.hashedKeyModN),
                             len(value),
                             value,
                             threading.currentThread(), random_node, retrials=2)
        response_code, value_biggy = settings.wireObj_push_alive.receive_reply(threading.currentThread(), Command.PUSH)
        if response_code == Response.SUCCESS:
            increment_soft_state(str(random_node))
            value_biggy = value_biggy.split(',')
            update_incoming(value_biggy)
        contaminated = False


def other_alive_node(sender="-1"):  # exclude sender as well
    if len(settings.aliveNessTable.hashTable) > 0:
        # tmp = random.randint(0, len(settings.aliveNessTable.hashTable) - 1)
        return random.choice(settings.aliveNessTable.hashTable.keys())
    else:
        tmp = random.randint(0, int(settings.N) - 1)
        if tmp == int(settings.hashedKeyModN) or tmp == int(sender):
                return other_alive_node()
        else:
            return int(tmp)


def i_am_alive_small_network():
    while True:
        time.sleep(2)
        # print "i_am_alive_small_network"
        random_node = other_alive_node()
        value = settings.aliveNessTable.get_list_of_alive_keys()
        value = ",".join(value)
        settings.wireObj_push_alive.send_request(Command.PUSH, str(settings.hashedKeyModN),
                             len(value),
                             value,
                             threading.currentThread(), random_node, retrials=2)
        response_code, value_biggy = settings.wireObj_push_alive.receive_reply(threading.currentThread(), Command.PUSH)
        if response_code == Response.SUCCESS:
            increment_soft_state(str(random_node))
            value_biggy = value_biggy.split(',')
            update_incoming(value_biggy)


def i_am_alive_gossip():
        randomNode = other_node()
        settings.wireObj_push_alive.send_request(Command.ALIVE, str(settings.hashedKeyModN), 0, "", threading.currentThread(), randomNode, retrials=2)
        response_code, value = settings.wireObj_push_alive.receive_reply(threading.currentThread(), Command.ALIVE)
        if response_code == Response.SUCCESS:
            increment_soft_state(str(randomNode))


# Decrement the soft state
def decrement_soft_state():
    while True:
        if int(settings.N) > 10:  # for the 50 nodes
            time.sleep(10)
            step = 1
        else:
            time.sleep(2)
            step = 1

        for k in settings.aliveNessTable.hashTable:
            if settings.aliveNessTable.get(k) - step < -1:  # min =-1
                settings.aliveNessTable.put(k, -1)
            else:
                settings.aliveNessTable.put(k, settings.aliveNessTable.get(k) - step)

        # Cleanup -1
        remove = [k for k, v in settings.aliveNessTable.hashTable.items() if v == -1]
        for k in remove: del settings.aliveNessTable.hashTable[k]