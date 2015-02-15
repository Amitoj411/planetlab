__author__ = 'Owner'
import udpSendRecieve


class Wire:
    numberOfNodes = 0
    description = "This is implemented on top of the request/reply protocol you developed for A1 " \
                  "(i.e., using UDP, the process for unique IDs, timeouts, etc). " \
                  " The following describes the format of the application level messages exchanged using that protocol"
    def __init__(self, numberOfNodes):
        self.numberOfNodes = numberOfNodes

    def lookUp(self, hashedKeyMod): # (i.e.) key=apple return the port 50000
        _file = open('node_list.txt', 'rU')
        nodes = _file.readlines()

        for line in nodes:
            _arr = line.split(',')
            if hashedKeyMod == _arr[0].strip():
                return _arr[1].strip()

        return -1

        #  1. Command is 1 byte long. It can be:
        #     0x01. This is a put operation.
        #     0x02. This is a get operation.
        #     0x03. This is a remove operation.
        #     [Note: We may add some management operations, the message format will stay the same. For example:]
        #     0x04. Command to shutdown the node (think of this as an announced failure).
        #            The operation is asynchronous: returning success means that the node acknowledges receiving
        #            the command at it will shutdown as soon as possible.
        #     anything > 0x20. Your own commands if you want.
        # 2. The key is 32 bytes long. This is the identification of the value.
        # 3. The length of the value: integer represented on two bytes.  Maximum value 15,000.
        #    Only used for put operation.
        # 4.  Value. Byte array. Only used for put operation.
    def send(self, port, command, key, value_length, value):
        # @Abraham and Amitoj: pack the variable msg with the headers before sending
        msg = command + key + value_length + value
        #Get the IP from the key
        port = self.lookUp(hash(key)%self.numberOfNodes) # Will be changed later to return the IP
        obj = udpSendRecieve.UDPNetwork()
        obj.send("127.0.0.1", port, msg)

        # 1. The code is 1 byte long. It can be:
        # 0x00. This means the operation is successful.
        # 0x01.  Non-existent key requested in a get or delete operation
        # 0x02.  Out of space  (returned when there is no space left for a put).
        # 0x03.  System overload.
        # 0x04.  Internal KVStore failure
        # 0x05.  Unrecognized command.
        #      [possibly more standard codes will get defined here]
        # anything > 0x20. Your own error codes. [Define them in your Readme]
    def receive(self, hashedKeyMod):
        port = self.lookUp(hashedKeyMod)
        obj = udpSendRecieve.UDPNetwork()
        msg = obj.receive("127.0.0.1", port)
        # @Abraham and Amitoj: un-pack the variable msg from its headers before the return
        return msg

