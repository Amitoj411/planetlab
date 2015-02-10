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
    
    def parseExtraCommands():
#        with open('node_list.txt', 'rU') as f:
#               nodes = f.readlines()
        file=open('extra_commands.txt', 'rU')
        extraCommands = file.readlines()
        return extraCommands
    
    nodes=constructNodesArray()
    extraCommands=parseExtraCommands()
    N=len(nodes)
    saved=False
    
    args=str(sys.argv)

    print "len(nodes)=" + str(N)

    counter=0

    opts, args = getopt.getopt(sys.argv, "", [""])
    mode=args[1]

#    def workingNode(hostName):
#        file=open('node_dead_list.txt', 'rU')
#        nodesDead = file.readlines()
#        
#        file2=open('node_cant_login_list.txt', 'rU')
#        nodesCantLogin=file2.readlines()
#        
#        if(hostName in nodesDead or hostName in nodesCantLogin):
#            randomNode=randint(1,N)
#            newHostName=workingNode(nodes[randomNode-1]) # Dont come back until you find a working node
#        return newHostName

    def save_data(commands):
        #call (["ls", "-1"])
        #the next for many commands
        global saved
        if(~saved):
            #Retrieve node monitoring fields
            Nodes_IP = sub.Popen(''' /sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}' ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]
            Nodes_hostname = sub.Popen(''' hostname | awk '{printf $0}' ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]
            Nodes_du = sub.Popen(''' du -s | awk '{printf $0}' ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]
            Nodes_df = sub.Popen(''' df | awk '{printf $0}' ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]
            Nodes_uptime = sub.Popen(''' uptime | cut -d"," -f1 | awk '{printf $0}' ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]
            Nodes_alive = "True"
            Nodes_logon = "True"
            Nodes_load = sub.Popen(''' for avload in $(cat /proc/loadavg); do if [[ $avload =~ ^.*\\..*$ ]]; then echo -n  "$avload "; fi done ''', stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]

            Nodes_fields = [Nodes_IP, Nodes_hostname, Nodes_du, Nodes_df, Nodes_uptime, Nodes_alive, Nodes_logon, Nodes_load]
            output = ','.join(['"' + str(field) + '"' for field in Nodes_fields]) #CSV String of Node field data

            if commands is not None:
                Extra_commands = []
                for arg in commands:
                    command_output = sub.Popen(arg, stdout=sub.PIPE, stderr=sub.PIPE, shell=True).communicate()[0]
                    Extra_commands.append("<b>" + arg + "</b>"+ " : " + command_output)
                Extra_html = '<br><br>'.join([str(command_pair) for command_pair in Extra_commands]) #HTML Formatted String of Extra Commands
                output += ',"' + Extra_html + '"'
            else:
                output += ',""'

            print output
            # send it to the centralized server
            push("planetlab-01.vt.nodes.planet-lab.org",output,60006)
            saved=True
        

    def recieve():
        global mode
        print "waiting:"
        UDP_IP = "" #watch out from 127.0.0.1
        UDP_PORT = 5005

        sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        sock.bind((UDP_IP, UDP_PORT))

        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            print "received message: ", data
            if(data=="die"):
                mode="die"
            elif(data=="push"):
                mode="infected"
            break # you got to break!
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
#            print "Connecting to: "+UDP_IP #+ ", with the msg:" + MESSAGE
            sock.sendto(MESSAGE.rstrip(), (UDP_IP, UDP_PORT))
#            print "push is successful"
        except:
            print "push is not sccusseful\n"
            pass # the reciever should show you the dead nodes
            
#        print "UDP_host:"+ UDP_HOST + " UDP_IP: "+ UDP_IP







    #print "dsfdsfd" +infected

    while(counter<int(math.log(N,2))):
        print "Iteration: "+str(counter)
        if(mode=="infected"):
            save_data(extraCommands)
            randomNode=randint(1,N) #make sure it is not the same node as the current
            push(nodes[randomNode-1], "push", 5005)#2
        elif(mode=="notinfected"): 
            print "I'm not infected. Listening on port 5005.."
            recieved_counter=recieve() #keep waiting for infection msg
            save_data(extraCommands)
            randomNode=randint(1,N)
            push(nodes[randomNode-1], "push", 5005)#To-Do: make sure it is not the same node as the current
        elif(modeinfe=="die"):
            randomNode=randint(1,N) #make sure it is not the same node as the current
            push(nodes[randomNode-1], "die", 5005)#2
        counter=counter+1

    raise Exception("Terminated: Log(N) is reached")










