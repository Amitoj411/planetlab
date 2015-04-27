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
        The second is the id of the current node number [0 - 2^(N-1)]


#############################
## Sets of Test Nodes (96) ##
#############################
    THe following set of nodes have been deployed in one group of 96
    plonk.cs.uwaterloo.ca:33333
    planetlab1.csuohio.edu:33333
    kc-sce-plab2.umkc.edu:33333
    pl2.cs.unm.edu:33333
    planetlab2.cs.purdue.edu:33333
    ple2.ipv6.lip6.fr:33333
    planetlab2.koganei.itrc.net:33333
    ple4.ipv6.lip6.fr:33333
    ple6.ipv6.lip6.fr:33333
    planet1.pnl.nitech.ac.jp:33333
    planetlab1.koganei.itrc.net:33333
    planet-plc-1.mpi-sws.org:33333
    pl1.cs.montana.edu:33333
    planetlabtwo.ccs.neu.edu:33333
    75-130-96-13.static.oxfr.ma.charter.com:33333
    planetlabone.ccs.neu.edu:33333
    planetlab1.unr.edu:33333
    planetlab-5.eecs.cwru.edu:33333
    planetlab-01.bu.edu:33333
    planetlab1.dojima.wide.ad.jp:33333
    planetlab3.cesnet.cz:33333
    planetlab1.acis.ufl.edu:33333
    planetlab4.williams.edu:33333
    planetlab3.ucsd.edu:33333
    planetlab2.cis.upenn.edu:33333
    planetlab1.netlab.uky.edu:33333
    planetlab2.cs.colorado.edu:33333
    pl3.cs.unm.edu:33333
    planetlab1.cs.colorado.edu:33333
    pli1-pa-1.hpl.hp.com:33333
    plab4.eece.ksu.edu:33333
    pli1-pa-3.hpl.hp.com:33333
    planetlab1.unl.edu:33333
    pli1-pa-6.hpl.hp.com:33333
    planetlab1.net.in.tum.de:33333
    planetlab3.net.in.tum.de:33333
    planetlab2.netlab.uky.edu:33333
    planetlab1.otemachi.wide.ad.jp:33333
    planetlab1.tmit.bme.hu:33333
    peeramidion.irisa.fr:33333
    planetlab-2.fhi-fokus.de:33333
    node2.planetlab.mathcs.emory.edu:33333
    pl4.cs.unm.edu:33333
    plab4.ple.silweb.pl:33333
    sybaris.ipv6.lip6.fr:33333
    planetlab1.arizona-gigapop.net:33333
    planetlab1.eecs.umich.edu:33333
    planetlab2.ucsd.edu:33333
    planetlab1.ifi.uio.no:33333
    planetlab-1.fhi-fokus.de:33333
    flow.colgate.edu:33333
    host1.planetlab.informatik.tu-darmstadt.de:33333
    anateus.ipv6.lip6.fr:33333
    host2.planetlab.informatik.tu-darmstadt.de:33333
    inriarennes2.irisa.fr:33333
    iraplab1.iralab.uni-karlsruhe.de:33333
    pl2.cs.montana.edu:33333
    node2.planetlab.uni-luebeck.de:33333
    pl1.sos.info.hiroshima-cu.ac.jp:33333
    planetlab02.cs.washington.edu:33333
    planck227ple.test.ibbt.be:33333
    planetlab1.aut.ac.nz:33333
    planetlab1.cs.purdue.edu:33333
    planetlab1.informatik.uni-goettingen.de:33333
    planetlab-1.ssvl.kth.se:33333
    planet-lab2.cs.ucr.edu:33333
    planetlab2.ci.pwr.wroc.pl:33333
    planetlab2.ecs.vuw.ac.nz:33333
    planetlab2.informatik.uni-kl.de:33333
    planetlab3.rutgers.edu:33333
    planetlab5.csee.usf.edu:33333
    planetlab4.hiit.fi:33333
    planetlab-n1.wand.net.nz:33333
    planetlab-n2.wand.net.nz:33333
    planetvs2.informatik.uni-stuttgart.de:33333
    ple2.dmcs.p.lodz.pl:33333
    plnode-03.gpolab.bbn.com:33333
    plewifi.ipv6.lip6.fr:33333
    saturn.planetlab.carleton.ca:33333
    vn4.cse.wustl.edu:33333
    pl2.eng.monash.edu.au:33333
    planetlab3.mini.pw.edu.pl:33333
    planetlab1.cqupt.edu.cn:33333
    planetlab2.cs.uml.edu:33333
    planetlab-2.cse.ohio-state.edu:33333
    planetlab3.wail.wisc.edu:33333
    planetlab2.utdallas.edu:33333
    pl2.6test.edu.cn:33333
    salt.planetlab.cs.umd.edu:33333
    planetlab1.utdallas.edu:33333
    planetlab1.csee.usf.edu:33333
    planetlab-2.sjtu.edu.cn:33333
    planetlab1.cs.du.edu:33333
    planetlab-01.vt.nodes.planet-lab.org:33333
    planetlab1.mini.pw.edu.pl:33333
    pl1.6test.edu.cn:33333



##############################
## Sets of Test Nodes 1 x 3 ##
##############################
THe following sets of nodes have been deployed in groups of 3, isolated from the other sets.
    planetlab1.cs.ubc.ca:50000
    cs-planetlab3.cs.surrey.sfu.ca:50000
    planetlab2.cs.ubc.ca:50000


#######################
## Design
#######################
    Summary:
        The code runs consistent hashing to load balance the keys across the network.

    Membership protocol:
        We have implement Gossip-Style Failure Detection^1 membership protocol. Each node maintain route state in a routing table where it stores:
        node address (ID), HearBeat counter, time
        The Protocol works as follows:
            1-Regulary send HEARBEAT msgs to randomly selected nodes and update.
                If a node is alive increase the HeartBeat counter for that node by 1 and set Time field to time.now()
            2- Regulary (Tgossip):
                Sender:
                    DITRIBUTE the route table with other nodes using Gossip-style protocol.
                Receiver:
                    for all nodes info in DISTRIBUTE msg
                        if HeartBeat counter > the current HearBeat counter
                            set current HeartBeat counter to the maximum
                            set time to time.now()

        -A node will considered down if time.now() - node.time > Tfail.
        -If a node fails, no other nodes will update the HeartBeat counter for it and eventually  time.now() - node.time will be > Tfail.
        -After Tcleanup seconds, it will delete the member from the routing table
        -Why two different timeouts?
            To prevent oscillation: After Tfail, no new updates will be accepted for a node until Tcleanup. This will ensure that the state
            of that node will node be alive after a death just because another node still think it is alive
        - Tfail = 5 sec
        - Tcleanup = 10 sec
        - Tgossip = 2 sec

        Reference: https://courses.engr.illinois.edu/cs525/sp2011/L_member.sp11.ppt
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

    Optimizations:
        Quorum: Parrallel GET retrieval from all successors to improve Availability and enhance GET reliability. Also to decrease the latency.
        Client    SERVER 0         SERVER1       SERVER 2
           |         |                |            |
           X-------->|                |            |         Request: GET
           |<--------X                |            |         Response: Success
           |         X--------------->|----------->|         Request: Replicate GET
           |<-------------------------X            |         Response: Success
           |<--------------------------------------X         ResponsE: Success





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
REPLICATE_GET = 0x33
HEARTBEAT = 0x34
DISTRIBUTE = 0x35

#######################
## Requirements       #
#######################
- Python 2.5.1 or 2.7.8