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
import subprocess as sub


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
            os._exit(10)

        elif command == Command.JOIN:
            join_id = int(value)
            # print "Relieved Join ID:" + str(join_id)
            keys_to_be_deleted = []
            for key in kvTable.hashTable:
                if hash(key) % int(N) == join_id:  # ensure joinID is the ID of the predecessor
                    # print "Match Key:" + key
                    key_value = kvTable.hashTable[key]
                    wireObj.send_reply(sender_addr, "", Response.SUCCESS, 0, "")  # For th join
                    wireObj.send_request(Command.PUT, key, len(key_value), key_value, join_id)
                    response_code, value = wireObj.receive_reply()
                    if response_code == Response.SUCCESS:
                        keys_to_be_deleted.append(key)
                    else:
                        print "The joined node is dead for this key" + ", response: " + Response.print_response(response_code)
            for key in keys_to_be_deleted:
                kvTable.remove(key)



        else:
            response = Response.UNRECOGNIZED
            wireObj.send_reply(sender_addr, key, response, 0, "")


def user_input():
    while True:
        print "Main$ Please Enter one of the following:"
        print "     1- Print the local Key-value store:"
        print "     2- Get a value for a key (KV[key]):"
        print "     3- Put a value for a key (KV[key]=value):"
        print "     4- Remove a key from KV):"
        print "     5- Search for a key:"
        print "     6- Exit"
        nb = raw_input('>')
        if nb == "1":
            kvTable._print()
        elif nb == "2":  # GET
            key = raw_input('Main$ Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
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
                print "main$ response:" + Response.print_response(response)
            else:
                successor = nodeCommunicationObj.search(key, hashedKeyModN)
                if successor != -2:
                    # print "The Key Doesn't exist on the network, will return current node"
                    wireObj.send_request(Command.GET, key, 0, "", successor)
                    response_code, value = wireObj.receive_reply()
                    print "Main$ Response:" + Response.print_response(response_code), "Value:" + str(value[0])
                else:
                    # TODO Perhaps store key locally if no other nodes
                    response_code = Response.NoExternalAliveNodes
                    # wireObj.send_request(Command.GET, key, 0, "", -1)
                    print "Main$ Response:" + Response.print_response(response_code)
        elif nb == "3":  # PUT
            key = raw_input('Main$ Please enter the key>')
            value = raw_input('Main$ Please enter the value>')
            if hash(key) % int(N) == int(hashedKeyModN):
                try:
                    print "Main$ hash(%s) %% int(%d) == %d: , %d" % (key, int(N), hash(key) % int(N), hash(key))
                    kvTable.put(key, value)
                    print "Main$ KV[" + str(key) + "]=" + value
                    response = Response.SUCCESS
                except IOError:
                    response = Response.OUTOFSPACE
                except:
                    # response = Response.STOREFAILURE
                    raise
                print "Main$ response:" + Response.print_response(response)
                # wireObj.send_reply(key, response, 0, "")

            else:
                successor = nodeCommunicationObj.search(key, hashedKeyModN)
                if successor != -2:
                    print "$main: Next alive:" + str(successor)
                    wireObj.send_request(Command.PUT, key, len(value), value, successor)
                    response_code, value = wireObj.receive_reply()
                else:
                    # print "There is no nodes in the network"        #TODO Perhaps store key locally if no other nodes
                    response_code = Response.NoExternalAliveNodes
                    # wireObj.send_request(Command.PUT, key, len(value), value, -1)
                print "Response:" + Response.print_response(response_code)
                # sendAndWaitForAReplyThread = threading.Thread(target=sendAndWaitForAReply, args=(key, value))
                # sendAndWaitForAReplyThread.start()
        elif nb == "4": # remove
            key = raw_input('Main$ Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
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

                # wireObj.send_reply(key, response, 0, "")
                print "Main$ response:" + Response.print_response(response)
            else:
                wireObj.send_request(Command.REMOVE, key, 0, "", -1)
                response_code, value = wireObj.receive_reply()
                # print "Response:" + print_response(response_code)
        elif nb == "5":   # Exit
            key = raw_input('Main$ Please enter the key>')
            output = nodeCommunicationObj.search(key, hashedKeyModN)
            print "Main$ The Result is: " + str(output)
        else:
            # sys.exit("Exit normally.")
            os._exit(10)




if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv, "", [""])
    N = args[1]
    hashedKeyModN = args[2]

    kvTable = ring.Ring()
    wireObj = wire.Wire(int(N), hashedKeyModN)

    nodeCommunicationObj = AvailabilityAndConsistency.NodeCommunication(int(N))

    receiveThread = threading.Thread(target=receive_request)
    receiveThread.start()

    nodeCommunicationObj.join(int(hashedKeyModN)) # call joining procedure

    time.sleep(3)

    userInputThread = threading.Thread(target=user_input)
    userInputThread.start()

