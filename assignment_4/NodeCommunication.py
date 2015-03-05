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
    # Return: 'cursor' if you find a successor other than yourself
    # Return: '-2' if the local node is the successor or if you are only alive node in the network
    def search(self, key, localNode):
        hashedNodeID = hash(key) % self.numberOfNodes

        # Key Locally Stored - Preliminary check to see if you are the node the key should be stored on.
        if hashedNodeID == int(localNode):
            print "The Key should be stored locally"
            return localNode

        cursor = hashedNodeID           # Cursor goes through the range of nodes in our system
        while True:
            try:
                # Added to exclude yourself from being searched
                # If cursor is equal to localNode then return -2
                if cursor == int(localNode):
                    if cursor != 0:
                        cursor -= 1
                        if cursor == hashedNodeID:
                            return -2
                    else:
                        cursor = self.numberOfNodes - 1

                # Try to contact the cursor
                wireObj = wire.Wire(self.numberOfNodes, cursor)
                wireObj.send_request(Command.GET, key, 0, "", cursor)
                response_code, value = wireObj.receive_reply()
                print "Searched for node " + str(cursor) + " and received response: " + self.print_response(response_code)

                # If receive no reply from the cursor node, point cursor to the next node
                if response_code == Response.RPNOREPLY:
                    if cursor - 1 < 0:
                        cursor = self.numberOfNodes - 1
                    else:
                        cursor = (cursor - 1) % self.numberOfNodes

                    # Stop if you have looped back around to the original cursor
                    if cursor == hashedNodeID:
                        break

                # If we don't receive a timeout return the cursor i.e. it is a alive,
                # then return the cursor.
                else:
                    return cursor
            except:
                raise
        # Return -2 if
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
            print "successor found: " + str(successor)
            wire_obj = wire.Wire(self.numberOfNodes, successor)
            wire_obj.send_request(Command.JOIN, "anyKey", len(str(joinID)), str(joinID), successor)
            response_code, value = wire_obj.receive_reply()
            print "Response: " + self.print_response(response_code)

        print "Join synchronization is finished"



