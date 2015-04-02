__author__ = 'Owner'
# To-Do do whatever we did in assignment 1
import socket


class UDPNetwork:
    send_socket = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP

    def send(self, udp_ip, udp_port, message, RP_mode):
        # sock = socket.socket(socket.AF_INET,  # Internet
        #                      socket.SOCK_DGRAM)  # UDP
        if RP_mode == "server":
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #UDP  # Internet
            try:
                sock.sendto(message, (udp_ip, int(udp_port)))
            finally:
                sock.close()
        else:
            self.send_socket.sendto(message, (udp_ip, int(udp_port)))

    # Just for the receiver
    def reply(self, timeout):
        self.send_socket.settimeout(timeout)  # 100 ms be default
        while True:
            reply, addr = self.send_socket.recvfrom(1024)
            break
        return reply, addr

    def receive(self, udp_port, timeout, cur_thread, handler=""):  # udp_port to be removed after multi-threaded server is working fine
        if handler == "": # Single threaded serve
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("", int(udp_port)))
            sock.settimeout(timeout)  # 100 ms be default

            while True:
                data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes

                break
            return data, addr
        else:  # Multiple thread server
            # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # sock.bind(("", int(udp_port)))
            sock = handler.request[1]
            sock.settimeout(timeout)  # 100 ms be default
            while True:
                data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
                # print "Thread$:cur_thread.name" + cur_thread.name
                break
            # data = udp_thread.request[0].strip()
            # addr = udp_thread.client_address
            return data, addr