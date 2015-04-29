__author__ = 'Owner'
import socket


class UDPNetwork:
    def __init__(self, receiving_port=-1, middle_sender_addr=None):
        self.client_socket = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        self.server_socket = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        if receiving_port == -2:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # print middle_sender_addr
            self.server_socket.bind((middle_sender_addr, 0))  # only IP
        elif receiving_port != -1:
            try:
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind(('', int(receiving_port)))
            except:
                print receiving_port
                raise

    # Just for the client
    def send_request(self, udp_ip, udp_port, message):
        self.client_socket = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        self.client_socket.sendto(message, (udp_ip, int(udp_port)))
        # print self.client_socket.
        self.client_socket.getpeername

    # Just for the client
    def wait_reply(self, timeout):
        self.client_socket.settimeout(timeout)  # 100 ms be default
        while True:
            reply, addr = self.client_socket.recvfrom(2048)
            # print "BINGOOOO"
            break
        # self.server_socket.close()
        return reply, addr

    # Just for the server
    def send_reply(self, udp_ip, udp_port, message):
        self.server_socket.sendto(message, (udp_ip, int(udp_port)))


        # self.server_socket.close()

    # just for the server
    def receive_request(self):
        while True:
            # print cur_thread, '$', "wait"
            data, addr = self.server_socket.recvfrom(2048)  # buffer size is 1024 bytes
            break
        # self.server_socket.close()
        return data, addr
