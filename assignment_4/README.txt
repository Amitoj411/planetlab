#######################
## How to RUN
#######################
Modes:
    Local nodes:
        python main.py 3 0
        The first shell argument is the number of nodes in system
        The second is the id of the current node number (0-2^(n-1)).
    planetLab nodes:
        python main.py 3
        The first shell argument is the number of nodes in system
    testing:
        python main.py 3 0 testing
        The first shell argument is the number of nodes in system
        The second is the id of the current node number (0-2^(n-1)).

#######################
## Design
#######################
    Summary:
        The code runs consistent hasing to load balance the keys across the network.

    Failure:
        The Keys on the failed node are lost. However, any new keys that are supposed to assign to it will be
        redirected to successors

    Join:
        On joining the new node will check the successor to see if they had any keys related to its space. If yes,
        PUT them back to the joined node and remove the keys from the successor.

#######################
## User menu
#######################
The user has the option to choose one of the following:
Please Enter one of the following:
     1- Print the local Key-value store:
     2- Get a value for a key (KV[key]):
     3- Put a value for a key (KV[key]=value):
     4- Remove a key from KV):
     5- Search for a key:
     6- Shutdown
     7- Ping
     8- Exit


#######################
## CUSTOM Responses
#######################
RPNOREPLY: request reply is reporting dead server

#######################
## CUSTOM Commands
#######################
0x04: "SHUTDOWN"
0x20: "JOIN"
0x21: "PING"
