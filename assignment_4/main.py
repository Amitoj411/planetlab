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


# def sendAndWaitForAReply(key, value):
    # wireObj.send(Command.PUT, key, len(value), value)  # @Abraham & @Amitoj



def receive_request():
    while True:
        command, key, value_length, value, sender_addr = wireObj.receive_request(hashedKeyModN)  # type: request/reply
        # print "Receiving:" + command
        # @Michael: Please handle the msg
        # You might receive get or put msgs from other nodes.
        # Process the request locally and send them back the value in case of get
        if command == Command.PUT:
            try:
                kvTable.put(key, value)
                response = Response.SUCCESS
            except IOError:
                response = Response.OUTOFSPACE
            except:
                response = Response.STOREFAILURE

            wireObj.send_reply(sender_addr, key, response, 0, "")

        elif command == Command.GET:
            value_to_send = ""

            try:
                value_to_send = kvTable.get(key)
                response = Response.SUCCESS
            except KeyError:
                response = Response.NONEXISTENTKEY
            except MemoryError:
                response = Response.OVERLOAD
            except:
                response = Response.STOREFAILURE
            # print "value_to_send" + value_to_send
            wireObj.send_reply(sender_addr, key, response, len(value_to_send), value_to_send)
        #
        elif command == Command.REMOVE:
            try:
                kvTable.remove(key)
                response = Response.SUCCESS
            except KeyError:
                response = Response.NONEXISTENTKEY
            except MemoryError:
                response = Response.OVERLOAD
            except:
                response = Response.STOREFAILURE

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
            # print "Relieved Join ID:" + str(join_id)
            keys_to_be_deleted = []
            for key in kvTable.hashTable:
                if hash(key) % int(N) == join_id \
                        or (hash(key) % int(N) < join_id and hash(key) % int(N) < hashedKeyModN) \
                        or (hash(key) % int(N) > join_id):  # ensure joinID is the ID of the predecessor or the upper
                        # space between the joined node and the received node

                    key_value = kvTable.hashTable[key]
                    wireObj.send_request(Command.PUT, key, len(key_value), key_value, join_id)
                    response_code, value = wireObj.receive_reply(sender_addr)
                    if response_code == Response.SUCCESS:
                        keys_to_be_deleted.append(key)
                    else:
                        print "The joined node is dead for this key" + ", response: " + Response.print_response(response_code)
            for key in keys_to_be_deleted:
                kvTable.remove(key)

        else:
            response = Response.UNRECOGNIZED
            wireObj.send_reply(sender_addr, key, response, 0, "")


def try_to_get(key):
    value_to_send = ("", )
    try:
        value_to_send = kvTable.get(key)
        print "Main$ KV[" + str(key) + "]=" + kvTable.get(key)
        response = Response.SUCCESS
    except KeyError:
        response = Response.NONEXISTENTKEY
    except MemoryError:
        response = Response.OVERLOAD
    except:
        response = Response.STOREFAILURE
    return response, (value_to_send,)


def try_to_remove(key):
    try:
        value = kvTable.remove(key)
        print "Main$ Removing KV[" + str(key) + "]=" + value
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
        # print "Main$ hash(%s) %% int(%d) == %d: , %d" % (key, int(N), hash(key) % int(N), hash(key))
        kvTable.put(key, value)
        print "Main$ KV[" + str(key) + "]=" + value
        response = Response.SUCCESS
    except IOError:
        response = Response.OUTOFSPACE
    except:
        # response = Response.STOREFAILURE
        raise
    return response


def user_input():
    while True:
        print "Main$ Please Enter one of the following:"
        print "     1- Print the local Key-value store:"
        print "     2- Get a value for a key (KV[key]):"
        print "     3- Put a value for a key (KV[key]=value):"
        print "     4- Remove a key from KV):"
        print "     5- Search for a key:"
        print "     6- Shutdown"
        print "     7- Ping"
        print "     8- Exit"
        nb = raw_input('>')
        if nb == "1":
            kvTable._print()
        elif nb == "2":  # GET
            key = raw_input('Main$ Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                response_code, value = try_to_get(key)
            else:  # Not local
                successor = nodeCommunicationObj.search(key, hashedKeyModN)
                if successor != -2:
                    # print "The Key Doesn't exist on the network, will return current node"
                    if successor != int(hashedKeyModN):  # not the local node
                        wireObj.send_request(Command.GET, key, 0, "", successor)
                        response_code, value = wireObj.receive_reply("127.0.0.1:44444")  # We are not sending the TA
                        if response_code == Response.SUCCESS: print "Value:" + str(value[0])
                    else:  # the local node
                        response_code, value = try_to_get(key)
                else:
                    # TODO Perhaps store key locally if no other nodes: Yes
                    response_code, value = try_to_get(key)
                    if response_code != Response.SUCCESS:
                        response_code = Response.NoExternalAliveNodes
                        value = ("",)
            print "Main$ Response:" + Response.print_response(response_code)


        elif nb == "3":  # PUT
            key = raw_input('Main$ Please enter the key>')
            value = raw_input('Main$ Please enter the value>')
            if hash(key) % int(N) == int(hashedKeyModN):
                response_code = try_to_put(key, value)
            else:
                successor = nodeCommunicationObj.search(key, hashedKeyModN)
                if successor != -2:
                    print "$main: Next alive:" + str(successor)
                    if successor != int(hashedKeyModN):  # not the local node
                        wireObj.send_request(Command.PUT, key, len(value), value, successor)
                        response_code, value = wireObj.receive_reply("127.0.0.1:44444")  # We are not sending the TA
                    else:  # local
                        response_code = try_to_put(key, value)
                else:  # There is no nodes in the network"
                    # TODO Perhaps store key locally if no other nodes :YES
                    response_code = try_to_put(key, value)
            print "Response:" + Response.print_response(response_code)

        elif nb == "4":  # remove
            key = raw_input('Main$ Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                response_code = try_to_remove(key)
            else:
                successor = nodeCommunicationObj.search(key, hashedKeyModN)
                if successor != -2:
                    print "$main: Next alive:" + str(successor)
                    if successor != int(hashedKeyModN):  # not the local node
                        wireObj.send_request(Command.REMOVE, key, 0, "", successor)
                        response_code, value = wireObj.receive_reply("127.0.0.1:44444")  # We are not sending the TA
                    else:
                        response_code = try_to_remove(key)
                else:
                    # TODO Perhaps store key locally if no other nodes: Yes
                    response_code = try_to_remove(key)
                    if response_code != Response.SUCCESS:
                        response_code = Response.NoExternalAliveNodes
            print "Main$ response:" + Response.print_response(response_code)
        elif nb == "5":   # search
            key = raw_input('Main$ Please enter the key>')
            output = nodeCommunicationObj.search(key, hashedKeyModN)
            print "Main$ The Result is: " + str(output)
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
                    response_code, value = wireObj.receive_reply("127.0.0.1:44444")  # We are not sending the TA
                print "Main$ response:" + Response.print_response(response_code)
            else:
                node_id = raw_input('Main$ Please enter the node_id>')
                if int(node_id) == int(hashedKeyModN):
                    os._exit(10)
                    response_code = Response.SUCCESS
                else:
                    wireObj.send_request(Command.SHUTDOWN, "AnyKey", 0, "", node_id)
                    response_code, value = wireObj.receive_reply("127.0.0.1:44444")  # We are not sending the TA
                print "Main$ response:" + Response.print_response(response_code)
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
                    response_code, value = wireObj.receive_reply("127.0.0.1:44444")  # We are not sending the TA
                print "Main$ response:" + Response.print_response(response_code)
                if response_code == Response.SUCCESS: print "Reply:" + str(value[0])
            else:
                node_id = raw_input('Main$ Please enter the node_id>')
                if int(node_id) == int(hashedKeyModN):
                    value = ("Alive!",)
                    response_code = Response.SUCCESS
                else:
                    wireObj.send_request(Command.PING, "AnyKey", 0, "", node_id)
                    response_code, value = wireObj.receive_reply("127.0.0.1:44444")  # We are not sending the TA
                print "Main$ response:" + Response.print_response(response_code)
                if response_code == Response.SUCCESS: print "Reply:" + str(value[0])
        else:
            # sys.exit("Exit normally.")
            os._exit(10)




if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv, "", [""])
    N = args[1]
    mode = ""
    if len(args) > 2:
        hashedKeyModN = args[2]
        mode = Mode.local
    else:
        hashedKeyModN = NodeList.look_up_ip_address()
        mode = Mode.planetLab

    kvTable = ring.Ring()
    wireObj = wire.Wire(int(N), hashedKeyModN, mode)

    nodeCommunicationObj = AvailabilityAndConsistency.NodeCommunication(int(N), mode)

    receiveThread = threading.Thread(target=receive_request)
    receiveThread.start()

    nodeCommunicationObj.join(int(hashedKeyModN)) # call joining procedure

    time.sleep(2)

    userInputThread = threading.Thread(target=user_input)
    userInputThread.start()