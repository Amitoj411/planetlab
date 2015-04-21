__author__ = 'Owner'

import HashTable
import wire
import NodeList

def init(N_, hashedKeyModN_, mode_):

    global aliveNessTable
    aliveNessTable = HashTable.HashTable("AliveNess")

    global N
    N = N_

    global kvTable
    kvTable = HashTable.HashTable("KV", int(N))

    global hashedKeyModN
    hashedKeyModN = hashedKeyModN_

    #local or planetlab
    global mode
    mode = mode_

    global successor_list
    successor_list = [-1, -1]

    global wireObj
    ip_port = NodeList.look_up_node_id(hashedKeyModN, mode)
    receiving_port = ip_port.split(':')[1]
    wireObj = wire.Wire(int(N), hashedKeyModN, mode, "main", receiving_port, successor_list)

    global wireObj_replicate
    receiving_port = int(ip_port.split(':')[1]) + 500
    wireObj_replicate = wire.Wire(int(N), hashedKeyModN, mode, "replicate", receiving_port, successor_list)

    global wireObj_push_alive
    receiving_port = int(ip_port.split(':')[1]) + 1000
    wireObj_push_alive = wire.Wire(int(N), hashedKeyModN, mode, "epidemic", receiving_port, successor_list)

    global game_dag
    game_dag = HashTable.HashTable("game_dag", int(N))
    game_dag.put("game1", "1m:2m,2m:3c,3c:5c,5c:4c")
    # game_dag.put("game1", "1m:2m,2m:3c,3c:5c")

    # game_dag.put("game1", "1m:2m,2m:5c")