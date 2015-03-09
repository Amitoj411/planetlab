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
    fmtRequest = "<B32sH"  # Format of Data to be cont. later in the function
    fmtReply = "<BH"
    mode=""

    def __init__(self, numberOfNodes, hashedKeyModN, mode):
        self.numberOfNodes = numberOfNodes
        self.hashedKeyModN = hashedKeyModN #Local node only
        self.mode = mode
        # print ">>>>>>>>>>c" + str(hashedKeyModN)

    def send_request(self, command, key, value_length, value, node_overwrite):
        # @Abraham and Amitoj: pack the variable msg with the headers before sending
        fmt = self.fmtRequest
        if command == Command.PUT or command == Command.JOIN:
            fmt += str(value_length) + 's'
            msg = struct.pack(fmt, command, key, value_length, value)                #Packing value as an Int
        else:  # other commands
            fmt += '0s'  # hope to receive value of null with length 1
            msg = struct.pack(fmt, command, key, value_length, str(value))                  #Packing Key as an Int

        Print.print_("send_request$ command:" + Command.print_command(command) \
            + ", key: " + key \
            + ", value_length: " \
            + str(value_length)  \
            + ", value: " + str(value) \
            + ", node id: " + str(node_overwrite) \
            , Print.Wire, self.hashedKeyModN)

        #  Get the IP Port from the key
        if node_overwrite == -1:
            ip_port = NodeList.look_up_node_id(hash(key) % self.numberOfNodes, self.mode)
            # print Colors.Colors.OKGREEN  +"node_overwrite DISABLED and ip_port is: " + str(ip_port) + \
            # "  Message: " + str(msg)
        else:  # Get it by node id
            ip_port = NodeList.look_up_node_id(node_overwrite, self.mode)
            # print Colors.Colors.OKGREEN  +"node_overwrite ENABLED " + str(node_overwrite) + \
            # ", ip_port: " + str(ip_port) + ", Message: " + str(msg)

        local_ip_port = NodeList.look_up_node_id(self.hashedKeyModN, self.mode)
        self.RequestReplyClient_obj = RequestReplyClient.RequestReplyClient(ip_port.split(':')[0],
                                                                            ip_port.split(':')[1],
                                                                            msg,
                                                                            local_ip_port.split(':')[1],
                                                                            .1)

        self.RequestReplyClient_obj.send()

    def receive_request(self, hashedKeyMod):
        ip_port = NodeList.look_up_node_id(hashedKeyMod, self.mode)
        header, msg, addr = self.RequestReplyServer_obj.receive(ip_port.split(':')[1])

        try:
            command, key, value_length = struct.unpack(self.fmtRequest, msg[0:35])
            # print Colors.Colors.OKGREEN  +"receive_request command:" + str(command)
            if command == 0x01 or command == 0x20: #PUT or JOIN
                value_fmt = str(value_length) + 's'
                # print Colors.Colors.OKGREEN  +"command:" + self.print_command(command) + \
                #  ", key: " + key + ", value_length: " + str(value_length)
                # print Colors.Colors.OKGREEN  +"msg: " + msg
                value = struct.unpack(value_fmt, msg[35:35+value_length]) #Limit the max length of value to prevent buffer overflow attacks.
            else:  # Other commands
                value = ("",)

            Print.print_("receive_request$ "
                + str(addr)
                + ", Command Received:"
                + Command.print_command(command)
                + ", Key:"
                + key
                + ", Value: "
                + value[0]
                + ", Value Length: "
                + str(value_length)
                , Print.Wire, self.hashedKeyModN)
        except:
            raise

        # @Abraham and Amitoj: un-pack the variable msg from its headers before the return
        key = key.rstrip('\0')
        value = value[0]
        return command, key, value_length, value , addr

    def send_reply(self, sender_addr, key, response_code, value_length, value):
        # @Abraham and Amitoj: pack the variable msg with the headers before sending
        Print.print_(
            "send_reply$ " + str(sender_addr) +
            ", response_code: " + Response.print_response(response_code) +
            ", value: " + value +
            ", value length: " + str(value_length) +
            ", mode: " +
            Mode.print_mode(self.mode) +
            "\n", Print.Wire, self.hashedKeyModN)


        fmt = self.fmtReply
        fmt += str(value_length) + 's'
        msg = struct.pack(fmt, response_code, value_length, value)
        if self.mode == Mode.testing:
            self.RequestReplyServer_obj.send(sender_addr[0], sender_addr[1], msg)
        else:
            self.RequestReplyServer_obj.send(sender_addr[0], 44444, msg)

    def receive_reply(self, sender_addr):
        if self.mode == Mode.testing:
            request_reply_response = self.RequestReplyClient_obj.receive(sender_addr[1], self.hashedKeyModN)
        else:
            request_reply_response = self.RequestReplyClient_obj.receive(44444, self.hashedKeyModN)


        if request_reply_response == -1:
            response_code = Response.RPNOREPLY
            value = -1
        else:
            try:
                # request_reply_response = request_reply_response
                response_code, value_length = struct.unpack(self.fmtReply, request_reply_response[0:3])
                if response_code == 1 and value_length != 0:  # operation is successful and there is a value.
                    value_fmt = str(value_length) + 's'
                    value = struct.unpack(value_fmt, request_reply_response[3:])
                else:  # Other responses
                    value = ("",)
            except:
                raise

        Print.print_("receive_reply$ response:" + Response.print_response(response_code) + \
            ", value:" + str(value) + \
            ", mode: " + Mode.print_mode(self.mode) + "\n"\
            , Print.Wire, self.hashedKeyModN)
            
        return response_code, value

    # Server
    RequestReplyServer_obj = RequestReplyServer.RequestReplyServer(99999)  # listen infinitely

    # Client
    RequestReplyClient_obj = None
