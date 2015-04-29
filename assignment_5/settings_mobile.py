__author__ = 'Owner'

import HashTable

def init():

    global game_dag
    game_dag = HashTable.HashTable("game_dag")
    game_dag.put("game1", "1m:2m,2m:3c,3c:5c,5c:4c")
    # game_dag.put("game1", "1m:2m,2m:3c,3c:5c")

    # game_dag.put("game1", "1m:2m,2m:5c")