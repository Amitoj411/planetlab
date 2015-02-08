__author__ = 'Amitojsandhu'
#imports
from socket import *
import mysql.connector

Port = 8000
IP_Address = ''

def receiveData():
    #Setting up receive socket
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((IP_Address, Port))
    print("Listening on: ", IP_Address, "&", Port)
    #Receive messages
    while True:
        message, address = serverSocket.recvfrom(1024)
        print ("Connected to: ", address)
        #print ("Received Message: ", message)
        return message

def sendData(message):
    #Setting up sending socket
    sendSocket = socket(AF_INET, SOCK_DGRAM)
    sendSocket.connect((IP_Address, Port))
    
    #Send message
    sendSocket.send(message)
    print("Sent Data")


def convertData(message):
    
    convertedData = message + 'Hello'
    return convertedData

def mysqlConnector(message):
    #Connect to the MqSQL server
    conn = mysql.connector.connect(user="a7278452_group15", password="group15", host = "mysql11.000webhost.com", database="a7278452_nodes")
    mycursor = conn.cursor()
    
    #Try to data the file to the Database
    try:
        mycursor.execute("""INSERT INTO ..... VALUES (%s, %s)""", ())
        conn.commit()
    except:
        conn.rollback()


while True:
    msg = convertData(receiveData())
    print(msg)
    print(sendData(msg))