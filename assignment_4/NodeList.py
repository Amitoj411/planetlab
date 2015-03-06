__author__ = 'Owner'

import socket
# import struct
import Mode

fname_planet_lab = 'node_list_planetLab.txt'
fname_local = 'node_list_local.txt'

# For search, and for local mode
def look_up_node_id(hashedKeyMod, mode):  # (i.e.) if key=apple (node 0) return the ip:port
    if mode == Mode.local:
        _file = open(fname_local, 'rU')
        # print "local"
    else:
        _file = open(fname_planet_lab, 'rU')
        # print "planetLab"

    nodes = _file.readlines()

    for line in nodes:
        _arr = line.split(',')
        if int(hashedKeyMod) == int(_arr[0].strip()):
            return _arr[1].strip()

    return -1

# For planet lab mode only
# we only use it get the node id in planet lab mode initially instead of entering it as a SHELL argument
def look_up_ip_address():  # (i.e.) given the local IP return the ip:port
    _file = open(fname_planet_lab, 'rU')
    nodes = _file.readlines()

    ip_address = get_ip_address()

    for line in nodes:
        _arr = line.split(',')
        node_id = int(_arr[0].strip())
        _arr = _arr[1].split(':')
        if ip_address == _arr[0].strip():
            return node_id

    return -1


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    result = s.getsockname()[0]
    s.close()
    return result
