__author__ = 'Owner'
# To-Do do whatever we did in assignment 1
import socket


class UDPNetwork:
    send_socket = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP

    def send(self, udp_ip, udp_port, message):
        # sock = socket.socket(socket.AF_INET,  # Internet
        #                      socket.SOCK_DGRAM)  # UDP
        self.send_socket.sendto(message, (udp_ip, int(udp_port)))

    # Just for the sender
    def reply(self, timeout):
        self.send_socket.settimeout(timeout)  # 100 ms be default
        while True:
            reply, addr = self.send_socket.recvfrom(1024)
            break
        return reply, addr

    def receive(self, udp_port, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", int(udp_port)))
        sock.settimeout(timeout)  # 100 ms be default
        while True:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            break
        return data, addr


