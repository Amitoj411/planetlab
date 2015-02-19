#######################
## How to RUN
#######################
The first shell argument is the number of nodes in system
The second is the id of the current node number (0-2^(n-1)).

Ideally we will run
    python2.7 main.pyc 3 0
    python2.7 main.pyc 3 1
    python2.7 main.pyc 3 2
on the following three nodes, respectively:
    planetlab1.cs.ubc.ca
    planetlab2.cs.ubc.ca
    cs-planetlab3.cs.surrey.sfu.ca

For now just run
    python2.7 main.pyc 3 0

#######################
## User menu
#######################
The user has the option to choose one of the following:
Please Enter one of the following:
    1- Print the local Key-value store:
    2- Get a value for a key (KV[key]):
    3- Put a value for a key (KV[key]=value):
    4- Remove a key from (KV):
    5- Shutdown a Node
    6- (OR anything else) Exit


#######################
## CUSTOM RESPONSE
#######################
    -Response.RPNOREPLY: request reply is reporting dead server
