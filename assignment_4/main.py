__author__ = 'Owner'
import ring
import wire
import getopt
import sys
import threading
import Command
import Response
import os
import NodeCommunication
import subprocess as sub


# def sendAndWaitForAReply(key, value):
    # wireObj.send(Command.PUT, key, len(value), value)  # @Abraham & @Amitoj

def print_command(x):
    if x == 0x01:
        return "PUT"
    elif x == 0x02:
        return "GET"
    elif x == 0x03:
        return "REMOVE"
    elif x == 0x04:
        return "SHUTDOWN"
    elif x == 0x20:
        return "JOIN"

def receive_request():
    while True:
        command, key, value_length, value, sender_addr = wireObj.receive_request(hashedKeyModN)  # type: request/reply
        print "Receive thread reporting. Receiving from:" + str(sender_addr) + ", Command Recieved:" + print_command(command) + ", Value: " + value + ", Value Length: " + str(value_length)
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
            print "value_to_send" + value_to_send
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
            print "Recieved Join ID:" + str(join_id)
            for key in kvTable.hashTable:
                if hash(key) % int(N) == join_id: #ensure joinID is the ID of the predecessor
                    print "Match Key:" + key
                    key_value = kvTable.hashTable[key]
                    wireObj.send_request(Command.PUT, key, len(key_value), key_value, -1)
                    response_code, value = wireObj.receive_reply()
                    if response_code == Response.SUCCESS:
                        kvTable.remove(key)
                    else:
                        print "The joined node is dead" + ", respoonse: " + print_response(response_code)

            wireObj.send_reply(sender_addr, "", Response.SUCCESS, 0, "")





        else:
            response = Response.UNRECOGNIZED
            wireObj.send_reply(sender_addr, key, response, 0, "")


def user_input():
    while True:
        print "Please Enter one of the following:"
        print "     1- Print the local Key-value store:"
        print "     2- Get a value for a key (KV[key]):"
        print "     3- Put a value for a key (KV[key]=value):"
        print "     4- Remove a key from KV):"
        print "     5- Search for a key:"
        print "     6- Exit"
        nb = raw_input('>')
        if nb == "1":
            kvTable._print()
        elif nb == "2": # GET
            key = raw_input('Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                try:
                    value_to_send = kvTable.get(key)
                    print "KV[" + str(key) + "]=" + kvTable.get(key)
                    response = Response.SUCCESS
                except KeyError:
                    response = Response.NONEXISTENTKEY
                except MemoryError:
                    response = Response.OVERLOAD
                except:
                    response = Response.STOREFAILURE
                print "response:" + print_response(response) 
                # wireObj.send_reply(key, response, len(value_to_send), value_to_send)

            else:
                successor = nodeCommunicationObj.search(key, hashedKeyModN)
                if successor != -2:
                    print "The Key Doesn't exist on the network, will return current node"
                    wireObj.send_request(Command.GET, key, 0, "", successor)
                    response_code, value = wireObj.receive_reply()
                else:
                    print "There is no nodes in the network"    #TODO Perhaphs store key locally if no other nodes
                    response_code = Response.NoExternalAliveNodes
                    #wireObj.send_request(Command.GET, key, 0, "", -1)
                print "Response:" + print_response(response_code) , "Value:" + str(value[0])
        elif nb == "3":
            key = raw_input('Please enter the key>')
            value = raw_input('Please enter the value>')
            if hash(key) % int(N) == int(hashedKeyModN):
                try:
                    kvTable.put(key, value)
                    print "KV[" + str(key) + "]=" + value
                    response = Response.SUCCESS
                except IOError:
                    response = Response.OUTOFSPACE
                except:
                    response = Response.STOREFAILURE
                print "response:" + print_response(response) 
                # wireObj.send_reply(key, response, 0, "")

            else:
                successor = nodeCommunicationObj.search(key, hashedKeyModN)
                if successor != -2:
                    print "The Key Doesn't exist on the network, will return current node"
                    wireObj.send_request(Command.PUT, key, len(value), value, successor)
                    response_code, value = wireObj.receive_reply()

                else:
                    print "There is no nodes in the network"        #TODO Perhaphs store key locally if no other nodes
                    response_code = Response.NoExternalAliveNodes
                    #wireObj.send_request(Command.PUT, key, len(value), value, -1)
                print "Response:" + print_response(response_code) 
                # sendAndWaitForAReplyThread = threading.Thread(target=sendAndWaitForAReply, args=(key, value))
                # sendAndWaitForAReplyThread.start()
        elif nb == "4":
            key = raw_input('Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                try:
                    value = kvTable.remove(key)
                    print "Removing KV[" + str(key) + "]=" + value
                    response = Response.SUCCESS
                except KeyError:
                    response = Response.NONEXISTENTKEY
                except MemoryError:
                    response = Response.OVERLOAD
                except:
                    response = Response.STOREFAILURE

                # wireObj.send_reply(key, response, 0, "")
                print "response:" + print_response(response) 
            else:
                wireObj.send_request(Command.REMOVE, key, 0, "", -1)
                response_code, value = wireObj.receive_reply()
                print "Response:" + print_response(response_code) 
        elif nb == "5":
            key = raw_input('Please enter the key>')
            output = nodeCommunicationObj.search(key, hashedKeyModN)
            print "The Result is: " + str(output)
        else:
            # sys.exit("Exit normally.")
            os._exit(10)


def print_response(x):
    if x == 0x01:
        return "SUCCESS"
    elif x == 0x02:
        return "NONEXISTENTKEY"
    elif x == 0x03:
        return "OUTOFSPACE"
    elif x == 0x04:
        return "OVERLOAD"
    elif x == 0x05:
        return "STOREFAILURE"
    elif x == 0x06:
        return "UNRECOGNIZED"
    elif x == 0x21:
        return "RPNOREPLY"
    elif x == 0x22:
        return "NoExternalAliveNodes"

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv, "", [""])
    N = args[1]
    hashedKeyModN = args[2]

    kvTable = ring.Ring()
    wireObj = wire.Wire(int(N), hashedKeyModN)

    nodeCommunicationObj = NodeCommunication.NodeCommunication(int(N))

    receiveThread = threading.Thread(target=receive_request)
    receiveThread.start()

    userInputThread = threading.Thread(target=user_input)
    userInputThread.start()

    nodeCommunicationObj.join(int(hashedKeyModN)) # call joining procedure

