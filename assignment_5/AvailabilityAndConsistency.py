__author__ = 'Owner'
import wire

import Command
import Response
import Print
import threading


class NodeCommunication:
    numberOfNodes = 0
    mode = ""
    # aliveNessTable = [-2, -2 ,-2]
    def __init__(self, numberOfNodes, mode):
        self.numberOfNodes = numberOfNodes
        self.mode = mode
        # self.aliveNessTable = aliveNessTable
    # Given a key, the local nodeID of the first alive node is returned
    # Unless if it is a key the belongs to the local nodeID then return the local node id
    # The returned nodeID may or may not contain the specified key.
    # Use the returned nodeID to call subsequent operations.
    # Return: 'cursor' if you find a successor other than yourself
    # Return: '-2' if the local node is the successor or if you are only alive node in the network
    # TODO modify the search to use the aliveness table
    def search(self, key, localNode, aliveNessTable):
        print "search: "
        if len(aliveNessTable.items())>0:
            for v in aliveNessTable:
                print v
        localNode = int(localNode)
        cursor = hash(key) % self.numberOfNodes

        # Key Locally Stored - Preliminary check to see if you are the node the key should be stored on.
        if cursor == localNode:
            Print.print_("Local Key" + "\n",
                         Print.AvailabilityAndConsistency, localNode)
            return localNode

        # cursor = hashedNodeID           # Cursor goes through the range of nodes in our system
        while True:
            if cursor == localNode:
                print "stop: " + str(cursor)
                return localNode

            # Check if the cursor in the aliveness table first. If not alive, to Try to PING the cursor
            # wireObj = wire.Wire(self.numberOfNodes, localNode, self.mode)
            # wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), cursor)
            # response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PING)
            # Print.print_("Searched for node "+ str(cursor) \
            #     + " and received response: "+ Response.print_response(response_code) + "\n",
            #              Print.AvailabilityAndConsistency, localNode)

            # # If receive no reply from the cursor node, point cursor to the next node
            # if response_code == Response.RPNOREPLY:  # counter clock wise
            if cursor - 1 < 0:
                cursor = self.numberOfNodes - 1
            else:
                cursor = (cursor - 1) % self.numberOfNodes

            # After 3 nodes apart distance, get it from the table,
            if (localNode > cursor and localNode - cursor > 3) or \
                    (localNode < cursor and (self.numberOfNodes - cursor) + localNode > 3):
                    if aliveNessTable.get(str(cursor)) >= 0:
                        return cursor
                    Print.print_("Searching for Node[table]:  " + str(cursor) +
                                 ", Status: " + str(aliveNessTable.get(str(cursor))),
                                 Print.AvailabilityAndConsistency, localNode)
            else:
                wireObj = wire.Wire(self.numberOfNodes, localNode, self.mode)
                wireObj.send_request(Command.PING, key, 0, "", threading.currentThread(), cursor)
                response_code, value = wireObj.receive_reply(threading.currentThread(), Command.PING)
                Print.print_("Searched for node "+ str(cursor) \
                    + " and received response: "+ Response.print_response(response_code) + "\n",
                             Print.AvailabilityAndConsistency, localNode)
                # If time-out continue, else stop
                if response_code == Response.RPNOREPLY:
                    continue
                else:
                    result = cursor
                    break
            # If we don't receive a timeout return the cursor i.e. it is a alive,
            # then return the cursor.
            # else:
            #     return cursor

        return result

    # Given a node_id return the first alive successor
    def successor(self, localNode, aliveNessTable):
        print "successor: "
        # print self.aliveNessTable[0]
        if len(aliveNessTable.items())>0:
            for v in aliveNessTable:
                print v
        localNode = int(localNode)
        cursor = localNode
        while True:
            # decrement
            if cursor - 1 < 0:
                cursor = self.numberOfNodes - 1
            else:
                cursor = (cursor - 1) % self.numberOfNodes

            # stop after 3 nodes apart distance
            # TODO to be removed, no restriction
            # if localNode > cursor:
            #     if localNode - cursor > 3:
            #         result = -2
            #         break
            # elif (self.numberOfNodes - cursor) + localNode > 3:
            #         result = -2
            #         break

            # If Im the only node in the network then break and return the current node_id
            if cursor == localNode:
                result = localNode
                print "stop: " + str(cursor)
                break

            # Echo-reply
            # ToDo if distance is more than 3 just check the local table,
            # For distance > 3 Check if the cursor in the aliveness table first. If not alive, to Try to PING the cursor
            if (localNode > cursor and localNode - cursor > 3) or \
                    (localNode < cursor and (self.numberOfNodes - cursor) + localNode > 3):
                    if aliveNessTable.get(str(cursor)) >= 0:
                        return cursor
                    Print.print_("Searching for Node[table]:  " + str(cursor) +
                                ", Status: " + str(aliveNessTable.get(str(cursor))),
                                 Print.AvailabilityAndConsistency, localNode)
            else:
                wire_obj = wire.Wire(self.numberOfNodes, localNode, self.mode)
                Print.print_("Searching for Node[PING]:  " + str(cursor), Print.AvailabilityAndConsistency, localNode)
                wire_obj.send_request(Command.PING, "Anykey", 0, "", threading.currentThread(), cursor)
                response_code, value = wire_obj.receive_reply(threading.currentThread(), Command.PING)
                # print "Response: "+ Response.print_response(response_code)

                # If time-out continue, else stop
                if response_code == Response.RPNOREPLY:
                    continue
                else:
                    result = cursor
                    break
        return result

    # Join procedure:
    # 1- Get the successor
    # 2- Send JOIN msg to it: to check if it has any key that natches the joined node and PUT it back and then REMOVE it
    def join(self, localNode, aliveNessTable):
        successor = self.successor(localNode, aliveNessTable)  # search by node id
        # if successor != localNode and successor != -2:  # else its only me in the network
        if successor != localNode:  # else its only me in the network
            Print.print_("successor found: "+ str(successor) + "\n"
                         ,Print.AvailabilityAndConsistency, localNode)
            wire_obj = wire.Wire(self.numberOfNodes, localNode, self.mode)
            wire_obj.send_request(Command.JOIN_SUCCESSOR, "anyKey", len(str(localNode)), str(localNode)
                                  , threading.currentThread(), successor)
            response_code, value = wire_obj.receive_reply(threading.currentThread(), Command.JOIN_SUCCESSOR)

        # elif successor == -2:
        #     print "stopped after three searches"

        Print.print_("Join synchronization is finished"+ "\n"\
             ,Print.AvailabilityAndConsistency, localNode)



