__author__ = 'Amitojsandhu'
#imports
from socket import *

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

def sendData(message):
    #Setting up sending socket
    sendSocket = socket(AF_INET, SOCK_DGRAM)
    sendSocket.connect((IP_Address, Port))

    #Send message
    sendSocket.send(message)
    print("Sent Data")

while True:
    msg = receiveData()
    print(msg)

print(sendData("message"))