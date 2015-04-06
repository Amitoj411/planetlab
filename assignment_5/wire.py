__author__ = 'Owner'
import RequestReplyClient
import RequestReplyServer
import struct
import Command
import Response
# import binascii
import Colors
import NodeList
import Mode
import Print

class Wire:
    description = "This is implemented on top of the request/reply protocol you developed for A1 " \
                  "(i.e., using UDP, the process for unique IDs, timeouts, etc). " \
                  " The following describes the format of the application level messages exchanged using that protocol"
    numberOfNodes = 0
    hashedKeyModN = -1
    fmtRequest = "<B32s"  # Format of Data to be cont. later in the function
    fmtReply = "<B"
    mode = ""
    ALIVE_PUSH_DEBUG = True
    REPLICATE_DEBUG = True
    successor = []
    id = ""

    def __init__(self, numberOfNodes, hashedKeyModN, mode, id_, successor=[-1, -1]):
        self.numberOfNodes = numberOfNodes
        self.hashedKeyModN = hashedKeyModN #Local node only
        self.mode = mode
        self.successor = successor
        self.id = id_  # just to have separate port for alive and push msgs
        # print ">>>>>>>>>>c" + str(hashedKeyModN)

    def send_request(self, command, key, value_length, value, cur_thread, node_overwrite, timeout=.1, retrials=2):
        fmt = self.fmtRequest
        if command == Command.PUT or command == Command.JOIN_SUCCESSOR or command == Command.JOIN_PREDECESSOR or command == Command.ALIVE or command ==Command.PUSH or Command.PUT_HINTED or Command.REPLICATE_PUT:
            fmt += "H" + str(value_length) + 's'
            msg = struct.pack(fmt, command, key, value_length, value)
        else:  # other commands
            fmt += '0s'  # hope to receive value of null with length 1
            msg = struct.pack(fmt, command, key, value_length, str(value))

        if (self.REPLICATE_DEBUG and (command != Command.ALIVE and command != Command.PUSH))\
                or self.ALIVE_PUSH_DEBUG and (command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE)\
                or (command != Command.ALIVE and command != Command.PUSH and command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE):
            Print.print_(str(self.successor[0]) + "," + str(self.successor[1])
                    +"send_request$ command:" + Command.print_command(command) \
                    + ", key: " + key \
                    + ", value_length: " \
                    + str(value_length)  \
                    + ", value: " + str(value) \
                    + ", node id: " + str(node_overwrite) \
                    , Print.Wire, self.hashedKeyModN, cur_thread)

        #  Get the IP Port from the key
        if node_overwrite == -1:
            ip_port = NodeList.look_up_node_id(hash(key) % self.numberOfNodes, self.mode)
        else:  # Get it by node id
            ip_port = NodeList.look_up_node_id(node_overwrite, self.mode)

        local_ip_port = NodeList.look_up_node_id(self.hashedKeyModN, self.mode)
        if self.id == "epidemic":
            port = int(ip_port.split(':')[1]) + 1000
            # print "epidemic"
        elif self.id == "replicate":
            port = int(ip_port.split(':')[1]) + 500
        else:
            port = ip_port.split(':')[1]
        self.RequestReplyClient_obj = RequestReplyClient.RequestReplyClient(ip_port.split(':')[0],
                                                                            port,
                                                                            msg,
                                                                            local_ip_port.split(':')[1],
                                                                            timeout,
                                                                            retrials,
                                                                            self.id)

        self.RequestReplyClient_obj.send()

    def receive_request(self, hashedKeyMod, cur_thread, handler=""):
        ip_port = NodeList.look_up_node_id(hashedKeyMod, self.mode)
        if self.id == "epidemic":
            port = int(ip_port.split(':')[1]) + 1000
            # print "epidemic"
        elif self.id == "replicate":
            port = int(ip_port.split(':')[1]) + 500
        else:
            port = ip_port.split(':')[1]
        header, msg, addr = self.RequestReplyServer_obj.receive(port, handler, cur_thread,
                                                                hashedKeyMod)

        try:
            command, key = struct.unpack(self.fmtRequest, msg[0:33])
            value_length = 0
            if command == Command.PUT or command == Command.JOIN_SUCCESSOR or command == Command.JOIN_PREDECESSOR or command == Command.ALIVE or command == Command.PUSH or command == Command.PUT_HINTED or command == Command.REPLICATE_PUT:
                value_length = struct.unpack("H", msg[33:35])
                value_length = int(value_length[0])
                # print value_length
                value_fmt = str(value_length) + 's'
                value = struct.unpack(value_fmt, msg[35:35 + value_length])
            else:  # Other commands
                value = ("",)

            if (self.REPLICATE_DEBUG and (command != Command.ALIVE and command != Command.PUSH))\
                or self.ALIVE_PUSH_DEBUG and (command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE)\
                or (command != Command.ALIVE and command != Command.PUSH and command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE):
                Print.print_(str(self.successor[0]) + "," + str(self.successor[1])
                        + "receive_request$ "
                        + str(addr)
                        + ", Command Received:"
                        + Command.print_command(command)
                        + ", Key:"
                        + key
                        + ", Value: "
                        + value[0]
                        + ", Value Length: "
                        + str(value_length)
                        , Print.Wire, self.hashedKeyModN, cur_thread)
        except:
            raise

        key = key.rstrip('\0')
        value = value[0]
        return command, key, value_length, value, addr

    def send_reply(self, sender_addr, key, response_code, value_length, value, cur_thread, command):

        if (self.REPLICATE_DEBUG and (command != Command.ALIVE and command != Command.PUSH))\
                or self.ALIVE_PUSH_DEBUG and (command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE)\
                or (command != Command.ALIVE and command != Command.PUSH and command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE):
            Print.print_(str(self.successor[0]) + "," + str(self.successor[1]) +
                "send_reply$ " + str(sender_addr) +
                ", response_code: " + Response.print_response(response_code) +
                ", value: " + value +
                ", value length: " + str(value_length) +
                ", mode: " +
                Mode.print_mode(self.mode) +
                "\n", Print.Wire, self.hashedKeyModN, cur_thread)

        fmt = self.fmtReply
        # Modify such that don't send the value length and the value except for teh GET PING and ALIVE
        if value_length != 0:
            fmt += 'H' + str(value_length) + 's'
            msg = struct.pack(fmt, response_code, value_length, value)
        else:
            msg = struct.pack(fmt, response_code)
        self.RequestReplyServer_obj.send(sender_addr[0], sender_addr[1], msg, command, key)

    def receive_reply(self, cur_thread, command):
        request_reply_response = self.RequestReplyClient_obj.receive_reply(command, self.hashedKeyModN, cur_thread)
        value = ("",)
        if request_reply_response == -1:
            response_code = Response.RPNOREPLY
        else:
            try:
                response_code = struct.unpack(self.fmtReply, request_reply_response[0:1])
                response_code = response_code[0]
                if response_code == Response.SUCCESS:
                    if len(request_reply_response) > 1:
                        value_length = struct.unpack('H', request_reply_response[1:3])
                        value_length = value_length[0]
                        if value_length != 0:  # operation is successful and there is a value.
                            value_fmt = str(value_length) + 's'
                            value = struct.unpack(value_fmt, request_reply_response[3:])
            except:
                raise
        if (self.REPLICATE_DEBUG and (command != Command.ALIVE and command != Command.PUSH))\
                or self.ALIVE_PUSH_DEBUG and (command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE)\
                or (command != Command.ALIVE and command != Command.PUSH and command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE):
            Print.print_(str(self.successor[0]) + "," + str(self.successor[1]) +
                "receive_reply$ response:" + Response.print_response(response_code) + \
                ", value:" + str(value[0]) + \
                ", mode: " + Mode.print_mode(self.mode) + "\n"\
                , Print.Wire, self.hashedKeyModN, cur_thread)
            
        return response_code, value[0]

    # Server
    RequestReplyServer_obj = RequestReplyServer.RequestReplyServer(99999, id)  # listen infinitely

    # Client
    RequestReplyClient_obj = None
