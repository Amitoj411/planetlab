__author__ = 'Owner'
import RequestReplyClient
import RequestReplyServer
import struct
import Command
import Response
import binascii


class Wire:
    description = "This is implemented on top of the request/reply protocol you developed for A1 " \
                  "(i.e., using UDP, the process for unique IDs, timeouts, etc). " \
                  " The following describes the format of the application level messages exchanged using that protocol"
    numberOfNodes = 0
    hashedKeyModN = -1
    fmtRequest = "<B32sH"  # Format of Data to be cont. later in the function
    fmtReply = "<BH"



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

    def send_request(self, command, key, value_length, value, node_overwrite):
        # @Abraham and Amitoj: pack the variable msg with the headers before sending
        fmt = self.fmtRequest
        if command == Command.PUT:
            fmt += str(value_length) + 's'
            msg = struct.pack(fmt, command, key, value_length, value)                #Packing value as an Int
        else:  # other commands
            fmt += '0s'  # hope to receive value of null with length 1
            msg = struct.pack(fmt, command, key, value_length, str(value))                  #Packing Key as an Int

        print "command: " + str(command) \
              + ", key: " + key \
              + ", value_length: " \
              + str(value_length)  \
              + ", value: " + str(value)

        print "msg: " + msg

        #  Get the IP Port from the key
        if node_overwrite == -1:
            ip_port = self.lookUp(hash(key) % self.numberOfNodes)  # Will be changed later to return the IP
            print "node_overwrite DISABLED and ip_port is: " + str(ip_port) + "  Message: " + str(msg)

        else:
            ip_port = self.lookUp(node_overwrite)  # Will be changed later to return the IP
            print "node_overwrite ENABLED " + str(node_overwrite) + "  ip_port: " + str(ip_port) + "  Message: " + str(msg)

        local_ip_port = self.lookUp(self.hashedKeyModN)
        self.RequestReplyClient_obj = RequestReplyClient.RequestReplyClient(ip_port.split(':')[0],
                                                                            ip_port.split(':')[1],
                                                                            msg,
                                                                            local_ip_port.split(':')[1],
                                                                            2)

        self.RequestReplyClient_obj.send()

    def receive_reply(self):
        request_reply_response = self.RequestReplyClient_obj.receive()

        if request_reply_response == -1:
            response_code= Response.RPNOREPLY
            value = -1
        else:
            try:
                # request_reply_response = binascii.unhexlify(request_reply_response)
                request_reply_response = request_reply_response
                response_code, value_length = struct.unpack(self.fmtReply, request_reply_response[0:3])
                if response_code == 1 and value_length != 0:  # operation is successful and there is a value.
                    value_fmt = str(value_length) + 's'
                    value = struct.unpack(value_fmt, request_reply_response[3:])
                else:  # Other commands
                    value = ("",)

            except:
                raise

        return response_code, value

    # Server functions:
    RequestReplyServer_obj = RequestReplyServer.RequestReplyServer(99999)  # listen infinitly

    def receive_request(self, hashedKeyMod):
        ip_port = self.lookUp(hashedKeyMod)
        header, msg, addr = self.RequestReplyServer_obj.receive(ip_port.split(':')[1])

        try:
            command, key, value_length = struct.unpack(self.fmtRequest, msg[0:35])
            if command == 1: #PUT
                value_fmt = str(value_length) + 's'
                print "command: " + str(command) + ", key: " + key + ", value_length: " + str(value_length)
                print "msg: " + msg
                value = struct.unpack(value_fmt, msg[35:])
            else:  # Other commands
                value = ("",)
        except:
            raise

        # @Abraham and Amitoj: un-pack the variable msg from its headers before the return
        key = key.rstrip('\0')
        value = value[0]
        return command, key, value_length, value , addr

    def send_reply(self, sender_addr, key, response_code, value_length, value):
        # @Abraham and Amitoj: pack the variable msg with the headers before sending
        print "send_reply: " + str(sender_addr) + ", response_code: " + str(response_code) + ", value: "+ value + ", value length: " + str(value_length)
        fmt = self.fmtReply
        fmt += str(value_length) + 's'
        msg = struct.pack(fmt, response_code, value_length, value)

        self.RequestReplyServer_obj.send(sender_addr[0], 44444, msg)


