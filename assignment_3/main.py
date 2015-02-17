__author__ = 'Owner'
import ring
import wire
import getopt
import sys
import threading
import Command

def receive():

while True:
    command, key, value_length, value = wireObj.receive(hashedKeyModN)
    print "Receive thread reporting..."
    print "Receiving:" + command
    # @Michael: Please handle the msg
    # You might receive get or put msgs from other nodes.
    # Process the request locally and send them back the value in case of get
    if command == "put":
        kvTable.put(key, value)
    elif command == "get":
        value_to_send = kvTable.get(key)
        wireObj.send("get", key, "", value_to_send)  # @Abraham & @Amitoj
	elif command = "remove":
		kvTable.remove(key)
	else
		print "Our own commands (whatever they may be)"

def user_input():
    while True:
        print "Please Enter one of the following:"
        print "     1- See the local Key-value store:"
        print "     2- Get a value for a key (KV[key]):"
        print "     3- Put a value for a key (KV[key]=value):"
        print "     4- Exit"
        nb = raw_input('>')
        if nb == "1":
            kvTable._print()
        elif nb == "2":
            key = raw_input('Please enter the key>')
            # Check if the key is stored locally else send a request
            if hash(key) % int(N) == int(hashedKeyModN):
                print "KV[" + key + "]=" + kvTable.get(key)
            else:
                wireObj.send(Command.GET, key, "", "")
        elif nb == "3":
            key = raw_input('Please enter the key>')
            value = raw_input('Please enter the value>')
            if hash(key) % int(N) == int(hashedKeyModN):
                kvTable.put(key, value)
                print "KV[" + key + "]=" + value
            else:
                wireObj.send(Command.PUT, int(key), len(value), int(value))  # @Abraham & @Amitoj
        else:
            sys.exit("Exit normally.")


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv, "", [""])
    N = args[1]
    hashedKeyModN = args[2]

    kvTable = ring.Ring()
    wireObj = wire.Wire(int(N))

    receiveThread = threading.Thread(target=receive)
    receiveThread.start()

    userInputThread = threading.Thread(target=user_input)
    userInputThread.start()




