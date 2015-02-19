__author__ = 'Owner'
import udpSendRecieve
import struct
import Command

class Wire:
    description = "This is implemented on top of the request/reply protocol you developed for A1 " \
                  "(i.e., using UDP, the process for unique IDs, timeouts, etc). " \
                  " The following describes the format of the application level messages exchanged using that protocol"
    numberOfNodes = 0
    fmt = "s" #Format of Data

    def __init__(self, numberOfNodes):
        self.numberOfNodes = numberOfNodes

    def lookUp(self, hashedKeyMod): # (i.e.) key=apple return the port 50000
        _file = open('node_list.txt', 'rU')
        nodes = _file.readlines()

        for line in nodes:
            _arr = line.split(',')
            if int(hashedKeyMod) == int(_arr[0].strip()):
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
    def send(self, command, key, value_length, value):
        # @Abraham and Amitoj: pack the variable msg with the headers before sending

        msg = struct.pack('B', command)               #Packing command as a single byte
        msg += struct.pack('I', key)                  #Packing Key as an Int

        if command == Command.PUT:
            msg += struct.pack('<I', value_length)      #Packing value_length as an Little Endian Int
            msg += struct.pack(self.fmt, value)                #Packing value as an Int

        # Get the IP:Port from the key
        port = self.lookUp(key%self.numberOfNodes) # Will be changed later to return the IP
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
        msg = obj.receive("", port)

        try:
            command = struct.unpack('B', msg[0])                  #Unpack the command which is an Integer (I)
            key = struct.unpack('I', msg[1:32])                   #Unpack the key which is an Int
            value_length = struct.unpack('<I', msg[33:35])      #Unpack the value_length which is a little endinan Int
            value = struct.unpack(msg[36:value_length])         #Unpack the value goes from Byte 36 to value_length

        except:
            # struct.error                                        #Produce error
            raise

        # @Abraham and Amitoj: un-pack the variable msg from its headers before the return
        #self.sendReply(port, command, response, value_length, value)

        return command, key, value_length, value

    def sendReply(self, key, response, value_length, value):
        # @Abraham and Amitoj: pack the variable msg with the headers before sending

        msg = struct.pack('B', response)               #Packing command as an Int

        if value_length > 0:
            msg += struct.pack('<I', value_length)      #Packing value_length as an Little Endian Int
            msg += struct.pack(self.fmt, value)                #Packing value as an Int

       # Get the IP:Port from the key
        port = self.lookUp(key%self.numberOfNodes) # Will be changed later to return the IP
        obj = udpSendRecieve.UDPNetwork()
        obj.send("127.0.0.1", port, msg)
