DROP TABLE Nodes;

CREATE TABLE Nodes
(Nodes_IP varchar(39) NOT NULL PRIMARY KEY,
Nodes_hostname varchar(50) NOT NULL,
Nodes_du INTEGER,
Nodes_df INTEGER,
Nodes_uptime INTEGER,
Nodes_alive BOOLEAN NOT NULL,
Nodes_logon BOOLEAN,
Nodes_load DECIMAL(3,2),
Nodes_extra varchar(50)
); 

INSERT INTO Nodes(Nodes_IP, Nodes_hostname, Nodes_du, Nodes_df, Nodes_uptime, Nodes_alive, Nodes_logon, Nodes_load) 
VALUES ('123.123.123', 'www.host1.com', 213, 112, 72, TRUE, TRUE, 0.40, 'none');