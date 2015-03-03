__author__ = 'Owner'

import wire
import Command
import Response

class NodeCommunication:
    numberOfNodes = 0

    def __init__(self, numberOfNodes):
        self.numberOfNodes = numberOfNodes

    #Given a key, the nodeID of the first alive node is returned.
    #The returned nodeID may or may not contain the specified key. Use the returned nodeID to call subsequent operations.
    def search(self, key):
        nodeID = hash(key) % numberOfNodes

        iNode = nodeID
        while iNode != nodeID:
            try:
                wireObj = wire.Wire(numberOfNodes, nodeID)
                wireObj.send_request(Command.GET, key, 0, 0)
                response_code, value = wireObj.receive_reply()

                if response_code == Response.RPNOREPLY:
                    iNode = (iNode - 1) % numberOfNodes
                else:
                    return iNode
                    break
            except:
                raise

        return None
