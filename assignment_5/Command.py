__author__ = 'Owner'

# Two groups waiting for a reply with a value
# PUT, REMOVE, SHUTDOWN, JOIN, PING, PUT_HINTED, REMOVE_HINTED
# GET, GET_HINTED, PUSH, ALIVE

PUT = 0x01
GET = 0x02
REMOVE = 0x03
SHUTDOWN = 0x04
JOIN_SUCCESSOR = 0x20
PING = 0x21
JOIN_PREDECESSOR = 0x22
PUSH = 0x23
ALIVE = 0x24

PUT_HINTED = 0x25
GET_HINTED = 0x26
REMOVE_HINTED = 0x27

REPLICATE_PUT = 0x28
REPLICATE_REMOVE = 0x29

# EXECUTE = 0x30
# RETURN = 0x31
EXECUTE = 0x30
# RPC_SIMULATE = 0x31
# RPC_REPLY = 0x32
REPLICATE_EXECUTE = 0x31
EXECUTE_HINTED = 0x32


REPLICATE_GET = 0x33

# New membership protocol
HEARTBEAT = 0x34
DISTRIBUTE = 0x35


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
        return "JOIN_SUCCESSOR"
    elif x == 0x21:
        return "PING"
    elif x == 0x22:
        return "JOIN_PREDECESSOR"
    elif x == 0x23:
        return "PUSH"  # anti-antropy
    elif x == 0x24:
        return "ALIVE"  # gossip
    elif x == 0x25:
        return "PUT_HINTED"  # gossip
    elif x == 0x26:
        return "GET_HINTED"
    elif x == 0x27:
        return "REMOVE_HINTED"
    elif x == 0x28:
        return "REPLICATE_PUT"
    elif x == 0x29:
        return "REPLICATE_REMOVE"
    elif x == 0x30:
        return "EXECUTE"
    # elif x == 0x31:
    #     return "RPC_SIMULATE"
    # elif x == 0x32:
    #     return "RPC_REPLY"
    elif x == 0x31:
        return "REPLICATE_EXECUTE"
    elif x == 0x32:
        return "EXECUTE_HINTED"


    elif x == 0x33:
        return "REPLICATE_GET"

    elif x == 0x34:
        return "HEARTBEAT"
    elif x == 0x35:
        return "DISTRIBUTE"



    else:
        return "UNRECOGNIZED"