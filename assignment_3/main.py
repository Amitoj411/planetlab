__author__ = 'Owner'
import ring
import wire
import getopt
import sys
import threading
import Command
import Response
import os


# def sendAndWaitForAReply(key, value):
    # wireObj.send(Command.PUT, key, len(value), value)  # @Abraham & @Amitoj


def receive():
    while True:
        type, command, key, value_length, value = wireObj.receive(hashedKeyModN)  # type: request/reply
        print "Receive thread reporting..."
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

            # wireObj.sendReply(key, response, 0, "")

        elif command == Command.GET:
            try:
                value_to_send = kvTable.get(key)
                response = Response.SUCCESS
            except KeyError:
                response = Response.NONEXISTENTKEY
            except MemoryError:
                response = Response.OVERLOAD
            except:
                response = Response.STOREFAILURE

            wireObj.sendReply(key, response, len(value_to_send), value_to_send)
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

            # wireObj.sendReply(key, response, 0, "")

        else:
            response = Response.UNRECOGNIZED
            # wireObj.sendReply(key, response, 0, "")


def user_input():
    while True:
        print "Please Enter one of the following:"
        print "     1- Print the local Key-value store:"
        print "     2- Get a value for a key (KV[key]):"
        print "     3- Put a value for a key (KV[key]=value):"
        print "     4- Remove a key from KV):"
        print "     5- Exit"
        nb = raw_input('>')
        if nb == "1":
            kvTable._print()
        elif nb == "2":
            key = raw_input('Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                print "KV[" + key + "]=" + kvTable.get(key)
            else:
                wireObj.send_request(Command.GET, key, len(""), "")
                response_code, value = wireObj.receive_reply()
                print "Response:" + response_code, "Value: " +value
        elif nb == "3":
            key = raw_input('Please enter the key>')
            value = raw_input('Please enter the value>')
            if hash(key) % int(N) == int(hashedKeyModN):
                kvTable.put(key, value)
                print "KV[" + key + "]=" + value
            else:
                wireObj.send_request(Command.PUT, key, len(value), value)
                response_code, value = wireObj.receive_reply()
                print "Response:" + response_code
                # sendAndWaitForAReplyThread = threading.Thread(target=sendAndWaitForAReply, args=(key, value))
                # sendAndWaitForAReplyThread.start()
        elif nb == "4":
            key = raw_input('Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                print "Removing KV[" + key + "]=" + kvTable.remove(key)
            else:
                wireObj.send_request(Command.REMOVE, key, len(""), "")
                response_code, value = wireObj.receive_reply()
                print "Response:" + response_code
        else:
            # sys.exit("Exit normally.")
            os._exit(10)


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv, "", [""])
    N = args[1]
    hashedKeyModN = args[2]

    kvTable = ring.Ring()
    wireObj = wire.Wire(int(N), hashedKeyModN)

    receiveThread = threading.Thread(target=receive)
    receiveThread.start()

    userInputThread = threading.Thread(target=user_input)
    userInputThread.start()
