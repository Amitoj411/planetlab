__author__ = 'Owner'
import RequestReplyClient
import RequestReplyServer
import struct
import Command
import Response


class Wire:
    description = "This is implemented on top of the request/reply protocol you developed for A1 " \
                  "(i.e., using UDP, the process for unique IDs, timeouts, etc). " \
                  " The following describes the format of the application level messages exchanged using that protocol"
    numberOfNodes = 0
    hashedKeyModN = -1
    fmtRequest = "<B32sI"  # Format of Data to be cont. later in the function
    fmtReply = "<BI"



    def __init__(self, numberOfNodes, hashedKeyModN):
        self.numberOfNodes = numberOfNodes
        self.hashedKeyModN = hashedKeyModN

    def lookUp(self, hashedKeyMod):  # (i.e.) key=apple return the port 50000
        _file = open('node_list.txt', 'rU')
        nodes = _file.readlines()

        for line in nodes:
            _arr = line.split(',')
            if int(hashedKeyMod) == int(_arr[0].strip()):
                return _arr[1].strip()

        return -1

    # Client functions:
    RequestReplyClient_obj = None

    def send_request(self, command, key, value_length, value):
        # @Abraham and Amitoj: pack the variable msg with the headers before sending
        fmt = self.fmtRequest
        if command == Command.PUT:
            fmt += str(value_length) + 's'
            msg = struct.pack(fmt, command, key, value_length, value)                #Packing value as an Int
        else:  # other commands
            fmt += '0s'  # hope to receive value of null with length 1
            msg = struct.pack(fmt, command, key, value_length, value)                  #Packing Key as an Int

        # print len(msg)
        #  Get the IP:Port from the key
        port = self.lookUp(hash(key) % self.numberOfNodes)  # Will be changed later to return the IP
        local_port = self.lookUp(self.hashedKeyModN)
        self.RequestReplyClient_obj = RequestReplyClient.RequestReplyClient("127.0.0.1", port, msg, local_port, .1)
        self.RequestReplyClient_obj.send()

    def receive_reply(self):
        request_reply_response = self.RequestReplyClient_obj.receive()
        if request_reply_response == -1:
            return Response.RPNOREPLY
        else:
            try:
                response_code, value_length = struct.unpack(self.fmtReply, request_reply_response[0:4])
                if response_code == 1 and value_length != 0:  # operation is successful and there is a value.
                    value_fmt = str(value_length) + 's'
                    value = struct.unpack(value_fmt, request_reply_response[5:])
                else:  # Other commands
                    value = ("",)

            except:
                raise

        return response_code, value

    # Server functions:
    RequestReplyServer_obj = RequestReplyServer.RequestReplyServer(99999)  # listen infinitly

    def receive_request(self, hashedKeyMod):
        port = self.lookUp(hashedKeyMod)
        header, msg = self.RequestReplyServer_obj.receive(port)

        try:
            command, key, value_length = struct.unpack(self.fmtRequest, msg[0:37])
            if command == 1: #PUT
                value_fmt = str(value_length) + 's'
                value = struct.unpack(value_fmt, msg[37:])
            else:  # Other commands
                value = ("",)
        except:
            raise

        # @Abraham and Amitoj: un-pack the variable msg from its headers before the return
        # self.sendReply(port, command, response, value_length, value)
        key = key.rstrip('\0')
        value = value[0]
        return command, key, value_length, value

    def send_reply(self, key, response_code, value_length, value):
        # @Abraham and Amitoj: pack the variable msg with the headers before sending

        fmt = self.fmtReply
        fmt += str(value_length) + 's'
        msg = struct.pack(fmt, response_code, value_length, value)

        #  if value_length > 0:
        #     msg += struct.pack('<I', value_length)      #Packing value_length as an Little Endian Int
        #     msg += struct.pack(self.fmt, value)                #Packing value as an Int

        #  Get the IP:Port from the key
        port = self.lookUp(hash(key)%self.numberOfNodes) # Will be changed later to return the IP
        self.RequestReplyServer_obj.send("127.0.0.1", port, msg)


