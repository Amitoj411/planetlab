import socket
#from random import randint
#from subproccess import call



def recieve():
    UDP_IP = ""
    UDP_PORT = 60006

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
	print "UDP: Listening on port 60006"
        data, addr = sock.recvfrom(2048) # buffer size is 1024 bytes
        print "received message:", data
	save_file(str(addr),data)
#    return recieved_couter

def save_file(addr,data):
	f = open(addr, "w")
	f.write( data  )      # str() converts to string
	f.close()



recieve();
