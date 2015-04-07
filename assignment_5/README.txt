#######################
## How to RUN        ##
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


#############################
## Sets of Test Nodes (50) ##
#############################
THe following set of nodes have been deployed in one group of 50
    0,plonk.cs.uwaterloo.ca:50000
    1,planetlab1.csuohio.edu:50000
    2,kc-sce-plab2.umkc.edu:50000
    3,pl2.cs.unm.edu:50000
    4,planetlab2.cs.purdue.edu:50000
    5,aguila2.lsi.upc.edu:50000
    6,planetlab2.koganei.itrc.net:50000
    7,aguila1.lsi.upc.edu:50000
    8,ricepl-2.cs.rice.edu:50000
    9,planet1.pnl.nitech.ac.jp:50000
    10,planetlab1.koganei.itrc.net:50000
    11,planetlab1.aut.ac.nz:50000
    12,host2.planetlab.informatik.tu-darmstadt.de:50000
    13,planetlab2.informatik.uni-erlangen.de:50000
    14,75-130-96-13.static.oxfr.ma.charter.com:50000
    15,planetlab-n1.wand.net.nz:50000
    16,planetlab1.unr.edu:50000
    17,planetlab2.informatik.uni-kl.de:50000
    18,planetlab1.informatik.uni-kl.de:50000
    19,planetlab1.dojima.wide.ad.jp:50000
    20,planetlab3.cesnet.cz:50000
    21,planetlab1.acis.ufl.edu:50000
    22,planetlab2.cqupt.edu.cn:50000
    23,planetlab-n2.wand.net.nz:50000
    24,planetlab2.cis.upenn.edu:50000
    25,planetlab1.netlab.uky.edu:50000
    26,planetlab1.utt.fr:50000
    27,pl3.cs.unm.edu:50000
    28,planetlab1.postel.org:50000
    29,pli1-pa-1.hpl.hp.com:50000
    30,planetlab1.cs.uiuc.edu:50000
    31,pli1-pa-3.hpl.hp.com:50000
    32,pl2.pku.edu.cn:50000
    33,planetvs2.informatik.uni-stuttgart.de:50000
    34,planetlab1.net.in.tum.de:50000
    35,planetlab3.net.in.tum.de:50000
    36,planetlab2.netlab.uky.edu:50000
    37,planetlab-2.scie.uestc.edu.cn:50000
    38,planetlab1.tmit.bme.hu:50000
    39,peeramidion.irisa.fr:50000
    40,planetlab-2.fhi-fokus.de:50000
    41,node2.planetlab.mathcs.emory.edu:50000
    42,pl4.cs.unm.edu:50000
    43,plab4.ple.silweb.pl:50000
    44,planetlab1.informatik.uni-goettingen.de:50000
    45,planetlab-1.sjtu.edu.cn:50000
    46,planetlab1.eecs.umich.edu:50000
    47,planetlab2.ucsd.edu:50000
    48,planetlab1.ifi.uio.no:50000
    49,planetlab1.bgu.ac.il:50000


##############################
## Sets of Test Nodes 6 x 3 ##
##############################
THe following sets of nodes have been deployed in groups of 3, isolated from the other sets.
    planetlab1.cs.ubc.ca:50000
    cs-planetlab3.cs.surrey.sfu.ca:50000
    planetlab2.cs.ubc.ca:50000

    planetlab2.cs.uml.edu:50000
    planetlab-2.cse.ohio-state.edu:50000
    planetlab3.wail.wisc.edu:50000

    lefthand.eecs.harvard.edu:50000
    planetlab2.utdallas.edu:50000
    pl2.6test.edu.cn:50000

    salt.planetlab.cs.umd.edu:50000
    planetlab1.utdallas.edu:50000
    planetlab1.csee.usf.edu:50000

    planetlab-2.sjtu.edu.cn:50000
    planetlab1.citadel.edu:50000
    planetlab1.cs.du.edu:50000

    planetlab-01.vt.nodes.planet-lab.org:50000
    planetlab1.mini.pw.edu.pl:50000
    pl1.6test.edu.cn:50000

    pl2.eng.monash.edu.au:50000
    planetlab3.mini.pw.edu.pl:50000
    planetlab1.cqupt.edu.cn:50000


#######################
## Design
#######################
    Summary:
        The code runs consistent hashing to load balance the keys across the network.

    Membership protocol:
        is implemented based on Epidemic algorithms; gossip is used as bootstrap to advertise new node joining the system.
        Anti-antropy is used to advertise the set of active nodes every three seconds. Once, a node receive an ALIVE msg
        from another, it increase the scale of aliveness by one (range from -1 to 3). -1 means dead and value above zero
        is alive. AliveNess table is maintained to store the aliveness value for each other node in the system (O(N)).
        An exception is mode once a node join a system and wants to find its successors and predecessors. In this case it use
        PING msgs up to three neighbors. Then it uses the AliveNess table to continue searching along the ring.


    Directions on the ring:
        - Counter clock wise to find a successor
        - Clock wise to find a predecessor

    Failure:
        The Keys on the failed node are replicated on a successor node. Hence, a node failure is transparent to the user.
        The system should work even with one node.

    Join:
        On joining, the new node will check the successors (Two; factor of 3) and predecessors to see if they had any
        "related keys" to its space. From successors it should get the local keys for the joining node and from the
        predecessors it should get the keys that are usually replicated to the joining node. Next, the successor/predecessor
        will PUT all the related keys back to the joined node while keeping it is own copy.

    Garbage collector-like process to handle replicated keys faraway from a predecessor:
        Suppose Nodes 0, 1, 2, 3, 4, 5, 6, and 7 in a system of size 8:
            All dead initially
            Node 1 join the system
            Node 0 join the system. Node 1 replicate some keys on node 0
            Node 5 join the system. Node 1 replicate some keys on both 0 and 5
            Node 7 join the system. Node 1 replicate some keys on both 0 and 7
        What would happen to 1's keys in node 3? A garbage collection like operation is needed.
        On node 3 the garbage collector will scan every 10s the keys that does not belong to it and check every key's orginal node.
        If all the successors of the original node are alive, move the send the keys to them and delete it locally.

    Replication:
        - Primary based and remote-write.
        - Non-blocking (PUT and REMOVE): Should always return SUCCESS
        - Blocking (GET): Might return SUCCESS or NONEXISTANCE key


#######################
## Testing
#######################
Four test files are provided with the same description provided in the course web page.
    test_5_response_time
    test_5_response_time_and_throughput
    test_5_single_node_failures
    test_5_catastrophic_failure


#######################
## User menu
#######################
The user has the option to choose one of the following:
Please Enter one of the following:
     1- Print the local Key-value store:            5- Search for a key:
     2- Get a value for a key (KV[key]):            6- Shutdown a node by (key/node_id):
     3- Put a value for a key (KV[key]=value):      7- Ping a node by (key/node_id):
     4- Remove a key from KV):                      8- Turn debugging msgs ON/OFF
     9- Print ServerCache                           10- Print Alive nodes
     11- print successor table                      Other- Exit



#######################
## CUSTOM Responses   #
#######################
RPNOREPLY: request reply is reporting dead server


#######################
## CUSTOM Commands    #
#######################
JOIN_SUCCESSOR = 0x20
PING = 0x21
JOIN_PREDECESSOR = 0x22
PUSH = 0x23
ALIVE = 0x24
PUT_HINTED = 0x25
GET_HINTED = 0x26
REMOVE_HINTED = 0x27
REPLICATE_PUT = 0x28
REPLICATE_REMOVE = 0x29

#######################
## Requirements       #
#######################
- Python 2.5.1 or 2.7.8