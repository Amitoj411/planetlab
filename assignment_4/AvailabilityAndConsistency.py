__author__ = 'Owner'
import wire

import Command
import Response
import Colors
import Print

class NodeCommunication:
    numberOfNodes = 0
    mode = ""

    def __init__(self, numberOfNodes, mode):
        self.numberOfNodes = numberOfNodes
        self.mode = mode

    # Given a key, the local nodeID of the first alive node is returned
    # Unless if it is a key the belongs to the local nodeID then return the local node id
    # The returned nodeID may or may not contain the specified key.
    # Use the returned nodeID to call subsequent operations.
    # Return: 'cursor' if you find a successor other than yourself
    # Return: '-2' if the local node is the successor or if you are only alive node in the network
    def search(self, key, localNode):
        cursor = hash(key) % self.numberOfNodes

        # Key Locally Stored - Preliminary check to see if you are the node the key should be stored on.
        if cursor == int(localNode):
            Print.print_("The Key should be stored locally"+ "\n",
                         Print.AvailabilityAndConsistency, localNode)
            return int(localNode)

        # cursor = hashedNodeID           # Cursor goes through the range of nodes in our system
        while True:
            try:
                # Added to exclude yourself from being searched
                # If cursor is equal to localNode then return -2
                # if cursor == int(localNode):
                #     if cursor != 0:
                #         cursor -= 1
                #         if cursor == hashedNodeID:
                #             return -2
                #     else:
                #         cursor = self.numberOfNodes - 1
                if cursor == int(localNode):
                    return int(localNode)

                # Try to contact the cursor
                wireObj = wire.Wire(self.numberOfNodes, localNode, self.mode) ####### BUGGGGGGGGGGGGGGGG
                wireObj.send_request(Command.PING, key, 0, "", cursor)
                response_code, value = wireObj.receive_reply("127.0.0.1:44444") # not replying to the TA
                Print.print_("Searching for node "+ str(cursor) \
                    + "and received response: "+ Response.print_response(response_code) + "\n",
                             Print.AvailabilityAndConsistency, localNode)

                # If receive no reply from the cursor node, point cursor to the next node
                if response_code == Response.RPNOREPLY:  # counter clock wise
                    if cursor - 1 < 0:
                        cursor = self.numberOfNodes - 1
                    else:
                        cursor = (cursor - 1) % self.numberOfNodes

                    # stop after 3 nodes apart distance
                    if int(localNode) > cursor:
                        if int(localNode) - cursor > 3:
                            return -2
                            break
                    elif (self.numberOfNodes - cursor) + int(localNode) > 3:
                            return -2
                            break
                    # Stop if you have looped back around to the original cursor
                    # if cursor == hashedNodeID:
                    #     break

                # If we don't receive a timeout return the cursor i.e. it is a alive,
                # then return the cursor.
                else:
                    return cursor
            except:
                raise
        return -2

    # Given a node_id return the first alive successor
    def successor(self, localNode):
        cursor = localNode
        while True:
            try:
                # print "node_id="+ str(node_id)
                # print "cursor="+ str(cursor)
                # decrement
                if cursor - 1 < 0:
                    cursor = self.numberOfNodes-1
                else:
                    cursor = (cursor - 1) % self.numberOfNodes

                # stop after 3 nodes apart distance
                if localNode > cursor:
                    if localNode - cursor > 3:
                        result = -2
                        break
                elif (self.numberOfNodes - cursor) + localNode > 3:
                        result = -2
                        break

                # If Im the only node in the network then break and return the current node_id
                if cursor == localNode:
                    result = localNode
                    break

                # Echo-reply
                wire_obj = wire.Wire(self.numberOfNodes, localNode, self.mode)
                Print.print_("Searching for Node:  "+ "\n"+\
                             str(cursor), Print.AvailabilityAndConsistency, localNode)
                wire_obj.send_request(Command.PING, "Anykey", 0, "", cursor)
                response_code, value = wire_obj.receive_reply("127.0.0.1:44444")  # Not sending back to the TA
                # print "Response: "+ Response.print_response(response_code)

                # If time-out continue, else stop
                if response_code == Response.RPNOREPLY:
                    continue
                else:
                    result = cursor
                    break
            except:
                raise

        return result

    # Join procedure:
    # 1- Get the successor
    # 2- Send JOIN msg to it: to check if it has any key that natches the joined node and PUT it back and then REMOVE it
    def join(self, localNode):
        successor = self.successor(localNode)  # search by node id
        if successor != localNode and successor != -2:  # else its only me in the network
            Print.print_("successor found: "+ str(successor) + "\n"
                         ,Print.AvailabilityAndConsistency, localNode)
            wire_obj = wire.Wire(self.numberOfNodes, localNode, self.mode) # BUGGGGGGGGGGGGGGGGGGGGG
            wire_obj.send_request(Command.JOIN, "anyKey", len(str(localNode)), str(localNode), successor)
            response_code, value = wire_obj.receive_reply("127.0.0.1:44444") # Not replying to the TA
        elif successor == -2:
            print "stopped after three searchs"

        Print.print_("Join synchronization is finished"+ "\n"\
             ,Print.AvailabilityAndConsistency, localNode)



