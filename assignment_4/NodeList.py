__author__ = 'Owner'

import socket
import struct

fname = 'node_list3.txt'

def look_up(hashedKeyMod):  # (i.e.) key=apple return the port 50000
    _file = open(fname, 'rU')
    nodes = _file.readlines()

    for line in nodes:
        _arr = line.split(',')
        if int(hashedKeyMod) == int(_arr[0].strip()):
            return _arr[1].strip()

    return -1

def get_node_id():  # (i.e.) key=apple return the port 50000
    _file = open(fname, 'rU')
    nodes = _file.readlines()

    ip_address = get_ip_address()

    for line in nodes:
        _arr = line.split(',')
        nodeID = int(_arr[0].strip())
        _arr = _arr[1].split(':')
        if ip_address == int(_arr[1].strip()):
            return nodeID

    return -1

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    return s.getsockname()[0]
