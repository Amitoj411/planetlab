__author__ = 'Owner'
import settings
import random
import threading
import Command
import Response
import wire
import time
import math
import VectorStamp
import HeartBeat
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

        elif command == Command.HEARTBEAT:
            response = Response.SUCCESS
            value = "Alive!"
            settings.wireObj_push_alive.send_reply(sender_addr, key, response, len(value), value, cur_thread, Command.HEARTBEAT, sixteen_byte_header)

            # Boost
            local_hb_obj = settings.aliveNessTable.get(key)
            if not local_hb_obj or time.time() - local_hb_obj.time >= settings.TClean:  # if not exist, add it
                HB = HeartBeat.HeartBeat(100000, time.time())
                settings.aliveNessTable.put(key, HB)
            else:  # compare heart beat
                # print "BONUS.. HEARTBEAT .. INCOMING", key
                local_hb_obj.heart_beat_counter += 1
                local_hb_obj.time = time.time()
                settings.aliveNessTable.put(key, local_hb_obj)

        elif command == Command.DISTRIBUTE:
            response = Response.SUCCESS
            value_to_send= "Alive!"
            settings.wireObj_push_alive.send_reply(sender_addr, settings.hashedKeyModN, response, len(value_to_send), value_to_send, cur_thread, Command.DISTRIBUTE, sixteen_byte_header)
            if value != "":
                remote_aliveness_table = value.split(',')
                for obj_str in remote_aliveness_table:
                    # print value
                    remote_node_id, remote_hear_beat_counter = obj_str.split(':')
                    if remote_node_id != settings.hashedKeyModN:
                        local_hb_obj = settings.aliveNessTable.get(remote_node_id)
                        if not local_hb_obj:
                            HB = HeartBeat.HeartBeat(100000, time.time())
                            settings.aliveNessTable.put(str(remote_node_id), HB)
                        else:  # compare heart beat
                            # if time.time() - local_hb_obj.time >= settings.TClean:  # if not exist, add it
                            #     HB = HeartBeat.HeartBeat(100000, time.time())
                            #     settings.aliveNessTable.put(str(remote_node_id), HB)
                            if time.time() - local_hb_obj.time <= settings.TFails:
                                if int(remote_hear_beat_counter) > local_hb_obj.heart_beat_counter:
                                    # second condition to prevent oscillation
                                    # if time.time() - local_hb_obj.time < settings.TClean:
                                    # print "BONUS .. DISTRIBUTE", remote_node_id
                                    local_hb_obj.heart_beat_counter = int(remote_hear_beat_counter)
                                    local_hb_obj.time = time.time()
                                    settings.aliveNessTable.put(str(remote_node_id), local_hb_obj)
                                # else:
                                    # # Since it is new, Distrubute logN , epdimcly
                                    # distribute("withoutIncrease")






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
        if int(settings.aliveNessTable.get(key)) + 1 > 6:  # max 3
            settings.aliveNessTable.put(key, 6)
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
                                 threading.currentThread(), randomNode, retrials=0)
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
            # r = random.randint(2, 3)  # periodically
            r = 2
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

# Decrement the soft state
def decrement_soft_state():
    while True:
        if int(settings.N) > 10:  # for the 50 nodes
            time.sleep(5)
            step = 2
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
        if int(settings.N) > 50:  # for the 50 nodes
            # time.sleep(3.5)
            continue
        if int(settings.N) > 10:  # for the 50 nodes
            # time.sleep(4)
            continue
        else:
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


def check_random_nodes():
    while True:
        need_to_advance = False
        # size = int(math.ceil(math.log(int(settings.N), 2)))
        size = int(math.log(int(settings.N), 2))
        range_ = range(0, int(settings.N))
        range_.remove(int(settings.hashedKeyModN))
        range_exclude_local = range_
        list_random_nodes = random.sample(range_exclude_local, size)
        for random_node in list_random_nodes:
            settings.wireObj_push_alive.send_request(Command.HEARTBEAT, str(settings.hashedKeyModN), len(""), "", threading.currentThread(), random_node, retrials=0)
            response_code, value_biggy = settings.wireObj_push_alive.receive_reply(threading.currentThread(), Command.HEARTBEAT)

            if response_code == Response.SUCCESS:
                local_hb_obj = settings.aliveNessTable.get(str(random_node))
                if not local_hb_obj or time.time() - local_hb_obj.time >= settings.TClean:  # does not exist, add it
                    HB = HeartBeat.HeartBeat(100000, time.time())
                    settings.aliveNessTable.put(str(random_node), HB)
                else:
                    local_hb_obj.heart_beat_counter += 1
                    local_hb_obj.time = time.time()
                    settings.aliveNessTable.put(str(random_node), local_hb_obj)
                    # print "BONUS ...HEARTBEAT.. OUTGOING", str(random_node)
            # else:
            #     settings.aliveNessTable.put(str(random_node), 0)
        time.sleep(settings.TlocalCheck)


def epidemically_send_local_route():
    time.sleep(1)  # just to populate the aliveness table first
    while True:
        distribute()
        time.sleep(settings.Tgossip) #Tgossip


def distribute():
    # Anti- Antropy
    # counter = 0
    # while counter < int(math.log(int(settings.N), 2)):
    sum_counter = 0
    while True:  # Send to log(settings.N) nodes
        counter = 0
        while counter < int(math.log(int(settings.N), 2)):
            random_node = other_node()
            value = settings.aliveNessTable.get_list_of_alive_keys()
            # value = ",".join(value)

            settings.wireObj_push_alive.send_request(Command.DISTRIBUTE, str(settings.hashedKeyModN), len(value), value,
                                 threading.currentThread(), random_node, .5, 0)
            response_code, value_biggy = settings.wireObj_push_alive.receive_reply(threading.currentThread(), Command.DISTRIBUTE)

            counter += 1

        sum_counter += counter
        k = 4
        probability_to_stop = 1.0 / k
        tmp = random.uniform(0.0, 1.0)
        if tmp < probability_to_stop:
            print "Gossip Stopped with prob (1/k=" + str(k) + "): " + str(tmp) + ". After " + str(sum_counter) + "  DISTRIBUTE msgs"
            break

# def clean_route_state():
#     while True:
#         items_to_clean = []
#         for k, obj in settings.aliveNessTable.hashTable.iteritems():
#             if time.time() - obj.time > settings.TClean:
#                 items_to_clean.append(k)
#
#
#         settings.aliveNessTable.remove(k)
#
#         time.sleep(3)