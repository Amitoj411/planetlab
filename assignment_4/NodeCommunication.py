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
        nodeID = hash(key) % self.numberOfNodes

        iNode = nodeID
        while True:                  #Have to fix because it won't run first time if !=
            try:
                wireObj = wire.Wire(self.numberOfNodes, iNode)
                wireObj.send_request(Command.GET, key, 0, "")
                response_code, value = wireObj.receive_reply()

                if response_code == Response.RPNOREPLY:
                    iNode = (iNode - 1) % self.numberOfNodes
                    if iNode == nodeID:
                        break;
                else:
                    return iNode
                    break
            except:
                raise

        return None

