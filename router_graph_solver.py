#!/usr/bin/python3

import configparser
import networkx
import sys
import ipaddress


#This class is used to store IP addresses used by a router
#to connect with other routers
class Router(object):
    def __init__(self, name):
        self.name=name
        self.connected_routers=[]
        self.ip_addresses=[]
    def connect_to_router(self, router_name, ip_address):
        if router_name in self.connected_routers:
            return
        self.connected_routers.append(router_name)
        self.ip_addresses.append(ip_address)
        print (self.name + " connected to " + router_name)
        print (self.ip_addresses)
    def get_description(self):
        print("Describing "+self.name)
        text=""
        num=len(self.connected_routers)
        for pos in range(0, num):
            r=self.connected_routers[pos]
            addr=self.ip_addresses[pos]
            text=text+"to "+r+" via "+str(addr)+"\n"
        return text
    def __str__(self):
        return self.name
    def get_name(self):
        return self.name
    def get_ip_to_find_router(self, router_name):
        total=len(self.connected_routers)
        for pos in range(0, total):
            if self.connected_routers[pos]==router_name:
                return self.ip_addresses[pos]
    
class RouterList:
    def __init__(self):
        self.routers=[]
        self.pos=0
    def append(self, router_object):
        self.routers.append(router_object)
        
    def __contains__(self, router_name):
        for r in self.routers:
            if r.get_name()==router_name:
                return True
        return False
    def get_router(self, router_name):
        for r in self.routers:
            if r.get_name()==router_name:
                return r
        return None
    def __iter__(self):
        return self
    def __next__(self):
        if self.pos<len(self.routers):
            i=self.pos
            self.pos=self.pos+1
            return self.routers[i]
        else:
            self.pos=0
            raise StopIteration()
    
        

def print_help():
    print ("\nUse: "+sys.argv[0]+" <file>")
    print ("Syntax error. Sections in <file> must have the syntax of A or B\n")
    print ("\t[A]")
    print ("\tnetwork_address=192.168.1.0/24")
    print ("\tnetwork_name=Madrid")
    print ("\trouter_name=R1")
    print ("\n")
    print ("\t[AS2]")
    print ("\tnetwork_address=192.168.2.0/24")
    print ("\trouter_1_name=R2")
    print ("\trouter_2_name=R3")
    print ("\tmetric=4 (optional, default value=1)")
    
    

def parse_section_as(section):
    try:
        network_address =   section['network_address']
        router_name     =   section['router_name']
    except KeyError:
        return False
    #If flow control is here, we are in a valid section
    #which describes a connection between a network and a router
    
    #Let's add the information to the graph
    metric=0
    edge=(network_address, router_name, metric)
    graph.add_weighted_edges_from( [edge] )
    
    #And we also add the network to a list
    networks.append(network_address)
    
    #And the router
    if not router_name in routers:
        r=Router(router_name)
        routers.append(r)
    return True
    
def parse_section_with_routers(section):
    try:
        network_address =   section['network_address']
        router_1_name   =   section['router_1_name']
        router_2_name   =   section['router_2_name']
        try:
            metric      =   section['metric']
        except KeyError:
            metric      =   1
    except KeyError:
        return False
    
    #If flow control is here, we are in a valid section
    #which describes a connection between a network and a router
    
    #Let's add the information to the graph
    metric=metric
    edge=(router_1_name, router_2_name, metric)
    graph.add_weighted_edges_from( [edge] )
    
    #Add the routers
    r1=None
    r2=None
    if router_1_name in routers:
        r1=routers.get_router(router_1_name)
    else:
        r1=Router(router_1_name)
        routers.append(r1)
    if router_2_name in routers:
        r2=Router(router_2_name)
        r2=routers.get_router(router_2_name)
    else:
        routers.append(r2)
    ip_addr=ipaddress.ip_network(network_address)
    r1.connect_to_router(router_2_name, ip_addr[1])
    r2.connect_to_router(router_1_name, ip_addr[2])
    return True

def parse_section(section):
    is_as_section=parse_section_as(section)
    if not is_as_section:
        is_routers_section=parse_section_with_routers(section)
        if not is_routers_section:
            print_help()
            print ("Erroneous section:"+str(section))


def create_routing_table(router, graph, networks):
    print ("Routing table for "+str(router))
    for network in networks:
        print (network)
        paths=networkx.all_simple_paths(graph, str(router), network)
        for p in paths:
            print (p)
    
#Main program
config=configparser.ConfigParser()
try:
    config.read(sys.argv[1])
except IndexError:
    print ("Error:No file given")
    
graph=networkx.Graph()
networks=[]
routers=RouterList()

for key in config:
    #configparser always has a DEFAULT section.
    #In this tool, DEFAULT is ignored
    if key!="DEFAULT":
        parse_section(config[key])

for router in routers:
    print (router.get_description())
    
for router in routers:
    #Fill the routing table for "router"
    #given a graph of interconnections
    #finding ways to the different networks
    create_routing_table(router, graph, networks)