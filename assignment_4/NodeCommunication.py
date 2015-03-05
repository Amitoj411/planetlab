__author__ = 'Owner'
import wire

import Command
import Response

class NodeCommunication:
    numberOfNodes = 0

    def __init__(self, numberOfNodes):
        self.numberOfNodes = numberOfNodes

    def print_response(self, x):
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

    #  Given a key, the nodeID of the first alive node is returned.
    # The returned nodeID may or may not contain the specified key.
    # Use the returned nodeID to call subsequent operations.
    def search(self, key, hashedKeyModN):
        nodeID = hash(key) % self.numberOfNodes

        if nodeID == int(hashedKeyModN):
            print "The Key is stored locally"
            return hashedKeyModN

        iNode = nodeID
        while True:
            try:
                wireObj = wire.Wire(self.numberOfNodes, iNode)

                #Added to exclude yourself from being searched
                if iNode == int(hashedKeyModN):
                    if iNode != 0:
                        iNode = iNode - 1
                        if iNode == nodeID:
                            return -2
                    else:
                        iNode = self.numberOfNodes-1

                wireObj.send_request(Command.GET, key, 0, "", iNode)
                print "Searching in Node:  " + str(iNode)
                response_code, value = wireObj.receive_reply()
                print "Response: " + self.print_response(response_code)

                if response_code == Response.RPNOREPLY:
                    if iNode - 1 < 0:
                        iNode = self.numberOfNodes-1
                    else:
                        iNode = (iNode - 1) % self.numberOfNodes

                    if iNode == nodeID:
                        break
                else:
                    return iNode                #Return iNode if the node is reachable i.e. No Timeout (RPNOREPLY)
            except:
                raise

        return -2

    def successor(self, node_id):
        cursor = node_id
        while True:
            try:
                if cursor - 1 < 0:
                    cursor = self.numberOfNodes-1
                else:
                    cursor = (cursor - 1) % self.numberOfNodes

                # If Im the only node in the network then break and return the current node_id
                if cursor == node_id:
                    result = node_id
                    break

                # Echo-reply
                wire_obj = wire.Wire(self.numberOfNodes, cursor)
                wire_obj.send_request(Command.GET, "Anykey", 0, "", cursor)
                print "Searching in Node:  " + str(cursor)
                response_code, value = wire_obj.receive_reply()
                print "Response: " + self.print_response(response_code)

                # If time-out continue, else stop
                if response_code == Response.RPNOREPLY:
                    continue
                else:
                    result = cursor
                    break
            except:
                raise

        return result

    def join(self, joinID):
        successor = self.successor(joinID)  # search by node id
        if successor != joinID:  # else its oly me in the network
            print "successor found: " + successor
            wire_obj = wire.Wire(self.numberOfNodes, successor)
            wire_obj.send_request(Command.JOIN, "", len(joinID), joinID, successor)
            response_code, value = wire_obj.receive_reply()
            print "Response: " + print_response(response_code) 

        print "Join synchronization is finished"



