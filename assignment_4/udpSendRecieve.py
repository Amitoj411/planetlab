__author__ = 'Owner'
# To-Do do whatever we did in assignment 1
import socket


class UDPNetwork:
    def send(self, udp_ip, udp_port, message):
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        sock.sendto(message, (udp_ip, int(udp_port)))

    def receive(self, udp_port, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", int(udp_port)))
        sock.settimeout(timeout)  # 100 ms be default
        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            break
        return data, addr


