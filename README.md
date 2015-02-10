A ‘readme’ file presenting your design choices for the monitoring service, its architecture, its limitations, and everything else you think is makes it stand out.
##################################
How To Run
##################################

Definitions:
-Infection seed: A node we picked arbitrary to start the infection: pl1.6test.edu.cn
-Storage server: A node we picked arbitrary to store the data messages from all the nodes on the network: planetlab-01.vt.nodes.planet-lab.org

Scenario 1 (Start the service):
1-If not running already, run the Storage server:
	 python reciever.py  & 
2- run the multicopy command on all the nodes on the slice except the infection seed
multiquery 'cd /tmp; python anti-entropy-push.py notinfected &'
3- On the infection seed:
python anti-entropy-push.py infected

Scenario 2 (Stop the service):
1-If not running already, run the Storage server:
	 python reciever.py  & 
2- run the multicopy command on all the nodes on the slice except the infection seed
multiquery 'cd /tmp; python anti-entropy-push.py notinfected &'
3- On the infection seed:
python anti-entropy-push.py die

Scenario 1 (Start the service with extra command):
1-If not running already, run the Storage server:
	 python reciever.py  & 
2- run the multicopy command on all the nodes on the slice except the infection seed with the extra command ‘uname -a’. The script would check a local file called ‘extra_commands.txt’ and parse it.
multicopy extra_commands.txt @:/tmp
multiquery 'cd /tmp; python anti-entropy-push.py notinfected &'
3- On the infection seed:
python anti-entropy-push.py infected

##################################
Design choices
##################################
Algorithm:
We have implemented an anti-entropy epidemic algorithm and run it successfully on the Planetlab slice for N nodes. We decide to use the push variant of the algorithm. Two type of  push messages are run by the algorithm:
Push infection: spread the infection to random node for Log(N) iterations
Push death: poison the death to random node for Log(N) iterations

In order to achieve the correctness of the algorithm we have to run over the active nodes. Active nodes are the ones that are ping-able and ssh-able. We used the multicopy command  over all the nodes which it basically run scp command  which in turn depends on ssh to access nodes and saved the log of the command. We parsed the log to check the dead and not accessible nodes. The total number of nodes in the slice are 1050 in which:
-187 are active nodes
-424 are active but not-accessible nodes through ssh 
-439 are dead nodes

Languages: 
Python, bash, mySQL, HTML

##################################
Epidemic protocol pseudo code
##################################
counter=0
mode=[”infected”, “notInfected”, “die”] # specified by the user
while(counter<log(N))
            if(mode=="infected")
           	 	save_data_if_not_saved()
            	push(randomNode, "mode=push")
            elif(mode=="notInfected")
           		mode=recieve() 
            	save_data_if_not_saved()
            	push(randomNode, "mode=push") 
            elif(mode=="die")
            	push(randomNode, "mode=die")
            counter=counter+1

    raise Exception("Terminated: Log(N) is reached")

##################################
Data Collection & storage
##################################
We pick one node to arbitrarily seed the infection. A UDP server is set to continuously listen for data messages and store data messages locally. A file with the host name is created on each node to store the results of the “node status” commands. The results of  the node status commands are stored in the following CSV format:

[Nodes_IP, Nodes_hostname, Nodes_du, Nodes_df, Nodes_uptime, Nodes_alive, Nodes_login, Nodes_load, Nodes_extra]

The CSV string is then sent through UDP to the database storage node. 

Our PlanetLab monitoring service supports extra bash commands in addition to the default node status commands. To execute extra commands, enter them in extra_commands.txt, separated by newlines.


##################################
Data parsing to SQL
##################################
A UDP server running Python code on ‘planetlab-01.vt.nodes.planet-lab.org’ receives data from all of the infected nodes.  Once it receives this data it uses a function to parse the received data in a format which mySQL will accept.  It then takes the parsed data and transmits it to our mySQL server.  It also deals with duplicate entries by removing older entries and making only the most recent entries available.

##################################
SQL server and DB Schema
##################################

Webhost ‘http://planetlabstatus.com/’ contains mySQL with remote host access capability, allowing for ‘planetlab-01.vt.nodes.planet-lab.org’ to access the database and insert elements to the tables. The database contains only one table, with columns corresponding to the ones seen on the web page. The host name is the primary key. 

##################################
Website
##################################
The data are parsed and presented as HTML on:
	http://planetlabstatus.com/
The website uses PHP in conjunction with mySQL to access the database, pull all of the data from it, then formats the data into an html format that is displayed as a neat table on the website. The PHP is run every time the web page is refreshed, so the data displayed is dynamic; the most recent version of the table is displayed when the webpage is opened. 

##################################
Limitations
##################################
1-We did not make our processes run indefinitely and flipping from ‘infected’ to ‘notInfected’ modes periodically because we thought it might take a lot of the slice’s resources and also it would make debugging more complicated. However, The not infected nodes are stalled on until they ‘receive’ an ‘infection’ msg or ‘die’ msg.  

