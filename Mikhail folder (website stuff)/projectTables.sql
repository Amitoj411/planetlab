drop table Nodes;

create table Nodes
(Nodes_IP varchar(39) not null PRIMARY KEY,
Nodes_hostname varchar(50) not null,
Nodes_du Integer,
Nodes_df Integer,
Nodes_uptime Integer,
Nodes_alive Boolean not null,
Nodes_logon Boolean,
Nodes_load Decimal(3,2)
); 
