__author__ = 'Amitojsandhu'
#imports
from socket import *
import MySQLdb
import datetime

Port = 60006
IP_Address = ''


def receiveData():
    
    #Setting up receive socket
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((IP_Address, Port))
    
    #Receive messages
    while True:
        message, address = serverSocket.recvfrom(2048)  #Size of 2048 bytes, may need to increase
        return message                                  #Returns the received message


#Not using this function - Sending to SQL server instead
def sendData(ip_name, port2, message):
    ip_addr = gethostbyname(ip_name)
    #Setting up sending socket
    sendSocket = socket(AF_INET, SOCK_DGRAM)
    sendSocket.connect((ip_addr, port2))
    #Send message
    sendSocket.send(message)


def mysqlConnector(message):
    #Connect to the MqSQL server
    conn = MySQLdb.connect("185.28.23.25", "planetla_group15", "group15", "planetla_Nodes")
    mycursor = conn.cursor()
    message_array = message.split(",")                          #Splits the incoming message by "," and creates a list instead
    
    current_time = str(datetime.datetime.now().time())                          #Added a timestamp
    print (current_time + "  Receiving Data from:  %s" % message_array[1])      #Prints the hostname that connected to it
    
    #Try to send data to the mySQL server
    try:
        mycursor.execute("""INSERT INTO nodes (nodes_IP, Nodes_hostname, Nodes_du, Nodes_df, Nodes_uptime, Nodes_alive, Nodes_login, Nodes_load, nodes_extra)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE Nodes_du=%s, Nodes_df=%s, Nodes_uptime=%s, Nodes_alive=%s, Nodes_login=%s, Nodes_load=%s, nodes_extra=%s""",
                         (message_array[0], message_array[1], message_array[2], message_array[3], message_array[4], message_array[5], message_array[6], message_array[7], message_array[8],
                          message_array[2], message_array[3], message_array[4], message_array[5], message_array[6], message_array[7], message_array[8]))
                          
        conn.commit()
    except:
        #       conn.rollback()
        raise

#    mycursor.execute("""SELECT * FROM nodes;""")   #Selects all the nodes in the table
#    print mycursor.fetchall()                      #Prints all the nodes


#***** All code executes here - Main *****#
print ("Listening on Port#:  %d" % Port)
while True:
    mysqlConnector(receiveData())