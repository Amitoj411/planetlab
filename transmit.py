#TODO: Implement mySQL, and finalize parsing

__author__ = 'Amitojsandhu'
#imports
from socket import *
#import mysql.connector

Port = 8000
IP_Address = ''


def receiveData():
    #Setting up receive socket
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((IP_Address, Port))
    #Receive messages
    while True:
        message, address = serverSocket.recvfrom(1024)
        print ("Connected to: ", address)
        #print ("Received Message: ", message)
        return message


#May not need this function - if we use SQL
def sendData(message):
    #Setting up sending socket
    sendSocket = socket(AF_INET, SOCK_DGRAM)
    sendSocket.connect((IP_Address, Port))
    
    #Send message
    sendSocket.send(message)
    print("Sent Data")


#Finis this...
def parseData(message):
    #message.find("....") <-- Returns the # from begining if found
    message2 = message.replace(" ", "")   #Eliminate whitesapce
    message_list = message2.split(",")
    return message_list


def mysqlConnector(message_list):
    #Connect to the MqSQL server
    print(message_list)
#    conn = mysql.connector.connect(user="a7278452_group15",
#                                   password="group15",
#                                   host = "mysql11.000webhost.com",
#                                   database="a7278452_nodes")
#    mycursor = conn.cursor()

#Try to data the file to the Database
#    try:
#Add variables and properly implement
#        mycursor.execute("""INSERT INTO ..... VALUES (%s, %s)""", ())
#        conn.commit()
#    except:
#        conn.rollback()

#All code executes here - Main
print "Listening IP Address: %s & Port # %d" % (IP_Address, Port)
while True:
    message_list = parseData(receiveData())
    print(message_list)
#mysqlConnector(message_list)
