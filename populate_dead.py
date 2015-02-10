import sys
import socket
import math
from random import randint
import getopt
#from subproccess import call
#os.system 
import subprocess as sub
import MySQLdb


db=MySQLdb.connect("185.28.23.25","planetla_group15","group15","planetla_Nodes")
#cur = db.cursor()
#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)




if __name__ == "__main__": 
    if(len(sys.argv) !=2 ): 
        raise Exception("Please enter:\n \
        mode: 'infected' or 'pure' ) #N: Number of nodes")
        
deadNodes = None
cantNodes = None

def constructNodesArray():
    global deadNodes
    global cantNodes
    file1=open('node_dead_list.txt', 'rU')
    deadNodes = file1.readlines()
    file2=open('node_cant_login_list.txt', 'rU')
    cantNodes = file2.readlines()
#        return nodes
    
    
constructNodesArray()

for node in deadNodes:
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Prepare SQL query to INSERT a record into the database.
    sql = """INSERT INTO nodes(node,IP)
             VALUES (%S, '99.99.99.99')"""
    try:
       # Execute the SQL command
       cursor.execute(sql, node)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       print "error in insert"
       db.rollback()

# disconnect from server
db.close()
  












