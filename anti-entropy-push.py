import sys
import socket
import math
from random import randint
import getopt
#from subproccess import call
#os.system 
import subprocess as sub

#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)


saved=False

if __name__ == "__main__": 
    if(len(sys.argv) !=2 ): 
        raise Exception("Please enter:\n \
        mode: 'infected' or 'pure' ) #N: Number of nodes")

    def constructNodesArray():
#        with open('node_list.txt', 'rU') as f:
#               nodes = f.readlines()
        file=open('node_list.txt', 'rU')
        nodes = file.readlines()

        return nodes
    #      for line in f:
    #         print 'Sending msg to host:'+line,
    #         push(recieved_couter+1)

    def save_data():
        #call (["ls", "-1"])
        #the next for many commands
        global saved
        if(~saved):
            #Retrieve node monitoring fields
            Nodes_IP = sub.Popen(''' /sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}' | ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]		
            Nodes_hostname = sub.Popen(''' hostname | awk '{printf $0}' ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]
            Nodes_du = sub.Popen(''' du -s | awk '{printf $0}' ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]
            Nodes_df = sub.Popen(''' df | awk '{printf $0}' ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]	
            Nodes_uptime = sub.Popen(''' uptime | cut -d"," -f1 | awk '{printf $0}' ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]
            Nodes_alive = True
            Nodes_logon = True
            Nodes_load = sub.Popen(''' for avload in $(cat /proc/loadavg); do if [[ $avload =~ ^.*\\..*$ ]]; then echo -n  "$avload "; fi done ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]
			
            Nodes_fields = [Nodes_IP, Nodes_hostname, Nodes_du, Nodes_df, Nodes_uptime, Nodes_alive, Nodes_logon, Nodes_load]
            output = ','.join([str(field) for field in Nodes_fields]) #CSV String of Node field data
			
            print output
            # send it to the centralized server
            push("planetlab-01.vt.nodes.planet-lab.org",output,6006)
            saved=True
        return 1

    def recieve():
        UDP_IP = "" #watch out from 127.0.0.1
        UDP_PORT = 5005

        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))

        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            print "received message:", data
        return data

    def push(UDP_HOST, MESSAGE, UDP_PORT):
        print "pushing to: " + UDP_HOST.rstrip() + ", the msg: " + MESSAGE.rstrip() + ", using port:" + str(UDP_PORT)
        #socket
    #    UDP_IP = "127.0.0.1"
    #    UDP_IP = nodes[randomNode]
#        UDP_PORT = 5005
    #    MESSAGE = "Hello, World!"
    #    MESSAGE = counter

#        print "UDP target IP:", UDP_IP
#        print "UDP target port:", UDP_PORT
#        print "message:", MESSAGE
        
        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        try:
            UDP_IP=socket.gethostbyname(UDP_HOST.rstrip())
            print "Connecting to: "+UDP_IP #+ ", with the msg:" + MESSAGE
            sock.sendto(MESSAGE.rstrip(), (UDP_IP, UDP_PORT))
            print "Push is successful"
        except:
            print "Push is not successful\n"
            pass # the reciever should show you the dead nodes
            
#        print "UDP_host:"+ UDP_HOST + " UDP_IP: "+ UDP_IP



    nodes=constructNodesArray()
    #print "Number of nodes: "+str(len(nodes))


    args=str(sys.argv)
    N=len(nodes)

    counter=0

    opts, args = getopt.getopt(sys.argv, "", [""])
    infected=args[1]
    #print "dsfdsfd" +infected

    while(counter<int(math.log(N,2))):
        print "Iteration: "+str(counter)
        if(infected=="infected"):
            save_data()#1
            randomNode=randint(1,N) #make sure it is not the same node as the current
            push(nodes[randomNode], "", 5005)#2
        else: 
            print "I'm pure"
            recieved_counter=recieve() #keep waiting for infection msg
            save_data()#1
            randomNode=randint(1,N)
            push(nodes[randomNode], "", 5005)#make sure it is not the same node as the current
            infected="infected"
        counter=counter+1

    raise Exception("Terminated: Log(N) is reached")
