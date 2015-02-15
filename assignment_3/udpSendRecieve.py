__author__ = 'Owner'
# To-Do do whatever we did in assignment 1
import socket


class UDPNetwork:
    # UDP_IP = "127.0.0.1"
    # UDP_PORT = 5005
    # MESSAGE = "Hello, World!"

    # def __init__(self, udp_ip, udp_port, message):
        # self.MESSAGE = message
        # self.UDP_IP = udp_ip
        # self.UDP_PORT = udp_port

    def send(self,  udp_ip, udp_port, message):
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        sock.sendto(message, (udp_ip, udp_port))

    def receive(self, udp_ip, udp_port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", int(udp_port)))

        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print "received message: ", data
            break
        return data


