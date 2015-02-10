__author__ = 'Amitojsandhu'
#imports
from socket import *
import MySQLdb

Port = 60006
IP_Address = ''


def receiveData():
    
    #Setting up receive socket
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((IP_Address, Port))
    
    #Receive messages
    while True:
        message, address = serverSocket.recvfrom(2048)  #Size of 2048 bytes, may need to increase
        #       print ("Connected to: ", address)               #Prints the address that connected to it
        return message                                  #Returns a list with [IP Address, Received Message]


#May not need this function - if we use SQL
def sendData(ip_name, port2, message):
    ip_addr = gethostbyname(ip_name)
    #Setting up sending socket
    sendSocket = socket(AF_INET, SOCK_DGRAM)
    sendSocket.connect((ip_addr, port2))
    #Send message
    sendSocket.send(message)


#Not using this
def parseData(message):
    #message.find("....")                           <-- Returns the # from beginning if found
    #message2 = message.replace(" ", "")            #Eliminate Whitesapce
    message_list = message.split(",")               #Splits string by ","
    print message
    #print'Uptime is: ', message_list               #Prints entire list seperated by ","
    #    uptime = float(message_list[5])                 #Converts string to float
    return message
#return message_list


def mysqlConnector(message):
    #Connect to the MqSQL server
    conn = MySQLdb.connect("185.28.23.25", "planetla_group15", "group15", "planetla_Nodes")
    mycursor = conn.cursor()
    message_array = message.split(",")
    print(message_array)
    
    #Try to send data the file to the Database
    try:
        mycursor.execute("""INSERT INTO nodes (nodes_IP, Nodes_hostname, Nodes_du, Nodes_df, Nodes_uptime, Nodes_alive, Nodes_login, Nodes_load, nodes_extra)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE Nodes_du=%s, Nodes_df=%s, Nodes_uptime=%s, Nodes_alive=%s, Nodes_login=%s, Nodes_load=%s, nodes_extra=%s""",
                         (message_array[0], message_array[1], message_array[2], message_array[3], message_array[4], message_array[5], message_array[6], message_array[7], message_array[8],
                          message_array[2], message_array[3], message_array[4], message_array[5], message_array[6], message_array[7], message_array[8]))
                          
        conn.commit()
    except:
        #print("Error in sending")
        #conn.rollback()
        raise

#    mycursor.execute("""SELECT * FROM nodes;""")    #Prints all the nodes
#    print mycursor.fetchall()


#***** All code executes here - Main *****#
print "Listening IP Address: %s & Port # %d" % (IP_Address, Port)
while True:
    mysqlConnector(receiveData())