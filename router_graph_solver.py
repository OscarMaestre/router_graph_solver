#!/usr/bin/python3

import configparser
import networkx
import sys

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
        network_name    =   section['network_name']
        router_name     =   section['router_name']
    except KeyError:
        return False
    #If flow control is here, we are in a valid section
    #which describes a connection between a network and a router
    
    #Let's add the information to the graph
    metric=1
    edge=(network_name, router_name, metric)
    graph.add_weighted_edges_from( [edge] )
    
    #And we also add the network to a list
    networks.append(network_name)
    
    #And the router
    routers.append(router_name)
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
    
    return True

def parse_section(section):
    is_as_section=parse_section_as(section)
    if not is_as_section:
        is_routers_section=parse_section_with_routers(section)
        if not is_routers_section:
            print_help()
            print ("Erroneous section:"+str(section))


#Main program
config=configparser.ConfigParser()
try:
    config.read(sys.argv[1])
except IndexError:
    print ("Error:No file given")
    
graph=networkx.Graph()
networks=[]
routers=[]
for key in config:
    #configparser always has a DEFAULT section.
    #In this tool, DEFAULT is ignored
    if key!="DEFAULT":
        parse_section(config[key])
