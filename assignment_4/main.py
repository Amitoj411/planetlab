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


def receive_request():
    while True:
        command, key, value_length, value, sender_addr = wireObj.receive_request(hashedKeyModN)  # type: request/reply
        print "Receive thread reporting. Receiving from:" + str(sender_addr)
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
                print "response:" + str(response)
                # wireObj.send_reply(key, response, len(value_to_send), value_to_send)

            else:
                wireObj.send_request(Command.GET, key, 0, "")
                response_code, value = wireObj.receive_reply()
                print "Response:" + str(response_code), "Value:" + str(value[0])
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
                print "response:" + str(response)
                # wireObj.send_reply(key, response, 0, "")

            else:
                wireObj.send_request(Command.PUT, key, len(value), value)
                response_code, value = wireObj.receive_reply()
                print "Response:" + str(response_code)
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
                print "response:" + str(response)
            else:
                wireObj.send_request(Command.REMOVE, key, 0, "")
                response_code, value = wireObj.receive_reply()
                print "Response:" + str(response_code)
        elif nb == "5":
            key = raw_input('Please enter the key>')
            output = nodeCommunicationObj.search(key)
            print "The Result is: " + str(output)
        else:
            # sys.exit("Exit normally.")
            os._exit(10)


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
