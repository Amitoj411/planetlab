#######################
## How to RUN
#######################
Modes:
    Local nodes: To run nodes locally.
        Syntax: python main.py 3 0
        The first shell argument is the number of nodes in system
        The second is the id of the current node number [0 - 2^(n-1)]

    PlanetLab nodes: To run nodes on planetLab. It differs from the Local mode by the way the node ids are obtained
        Syntax: python main.py 3
        The first shell argument is the number of nodes in system
        The second is the id of the current node number [0 - 2^(n-1)]

#######################
## Sets of Test Nodes
#######################
THe following sets of nodes have been deployed in groups of 3, isolated from the rest of the other nodes.

    planetlab2.cs.uml.edu
    planetlab-2.cse.ohio-state.edu
    planetlab3.wail.wisc.edu

    lefthand.eecs.harvard.edu
    planetlab2.utdallas.edu
    pl2.6test.edu.cn

    salt.planetlab.cs.umd.edu
    planetlab1.utdallas.edu
    planetlab1.csee.usf.edu

    planetlab-2.sjtu.edu.cn
    planetlab1.citadel.edu
    planetlab1.cs.du.edu

    planetlab-01.vt.nodes.planet-lab.org
    planetlab1.mini.pw.edu.pl
    pl1.6test.edu.cn

    pl2.eng.monash.edu.au
    planetlab3.mini.pw.edu.pl
    planetlab1.cqupt.edu.cn

    planetlab-1.ssvl.kth.se
    planetlab1.utt.fr
    planetlab2.cs.ubc.ca

#######################
## Design
#######################
    Summary:
        The code runs consistent hashing to load balance the keys across the network.
        No membership protocol is implemented; each time operation (PUT, GET, and REMOVE) need to be executed a
        PING command is sent to the node before the operation. If it failed, the command will be sent to first successor
        (target node -1; counter clockwise) up to 3 (Arbitrary selected).

    Failure:
        The Keys on the failed node are lost. However, any new keys that are supposed to be assigned to it will be
        redirected to successors (Up to 3)

    Join:
        On joining, the new node will check the successors (clockwise Up to 3) to see if they had any "related keys"
        to its space. Once it found a successor, it will stop. Next, the successor will PUT all the related keys back
        to the joined node and remove the related keys from the successor (if a SUCCESS reply is received from
        the joined node.

        Definition: "related keys" are the ones that hash to node id that is less than the successor node ideor more than the id
        of the joined node. This would cover the whole upper between joined node and the successor

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
     8- Turn debugging msgs ON/OFF
     9- Exit


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


#######################
## Requirements
#######################
- Python 2.5.1 or 2.7.8
- 1 second sleep for each iteration if huge list of keys were send to a node (Multi-threaded server
    is not implemented yet)
- Client must have a static external IP Address, not behind a NAT.
