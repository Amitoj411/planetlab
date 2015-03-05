__author__ = 'Owner'
import wire

import Command
import Response

class NodeCommunication:
    numberOfNodes = 0

    def __init__(self, numberOfNodes):
        self.numberOfNodes = numberOfNodes

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
                print "Response: " + str(response_code)

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

    def join(self, joinID):
        successor = self.search(joinID, "id")
        wireObj = wire.Wire(self.numberOfNodes, successor)
        wireObj.send_request(Command.JOIN, "", len(joinID), joinID, successor)
        response_code, value = wireObj.receive_reply()
