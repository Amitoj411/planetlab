__author__ = 'Owner'

PUT = 0x01
GET = 0x02
REMOVE = 0x03
SHUTDOWN = 0x04
JOIN = 0x20
PING = 0x21
# JOIN_FIN = 0x22
REPLICATE_PUT = 0x22
REPLICATE_REMOVE = 0x23

def print_command(x):
    if x == 0x01:
        return "PUT"
    elif x == 0x02:
        return "GET"
    elif x == 0x03:
        return "REMOVE"
    elif x == 0x04:
        return "SHUTDOWN"
    elif x == 0x20:
        return "JOIN"
    elif x == 0x21:
        return "PING"
    elif x == 0x22:
        return "REPLICATE_PUT"
    elif x == 0x23:
        return "REPLICATE_REMOVE"
    else:
        return "UNRECOGNIZED"

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