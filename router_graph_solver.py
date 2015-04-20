#!/usr/bin/python3

import configparser
import networkx
import sys
import ipaddress


LOGGING_ENABLED = False
ES="espanol"
EN="english"
LANGUAGE=ES
#This class is used to store IP addresses used by a router
#to connect with other routers
class Router(object):
    def __init__(self, name):
        self.name=name
        self.connected_routers=[]
        self.ip_addresses=[]
        self.routes=[]
    def connect_to_router(self, router_name, ip_address):
        if router_name in self.connected_routers:
            return
        self.connected_routers.append(router_name)
        self.ip_addresses.append(ip_address)
    def append_route(self, route):
        total=len(self.routes)
        #Check if route is a better route
        #than some of the router stored
        for pos in range(0, total):
            current_route=self.routes[pos]
            if route.can_replace(current_route) or route.is_better_than(current_route):
                if LOGGING_ENABLED:
                    print ( "{} replaced by {}".format(current_route, route))
                self.routes[pos]=route
                return
        if self.can_be_added(route):
            #The route can't replace any other route, so let's append the new route
            if LOGGING_ENABLED:
                print ("Added route "+str(route) + " for "+self.name)
            self.routes.append(route)
    
    #A route that uses the same gateway than other but with
    #a worse metric shouldn't be added
    def can_be_added(self, route):
        for r in self.routes:
            same_gw         = ( r.via             == route.via      )
            worse_metric    = ( route.metric       > r.metric       )
            same_destination= ( route.destination ==r.destination   )
            if same_gw and worse_metric and same_destination:
                return False
        return True
    
    def get_description(self):
        print("Router "+self.name)
        text=""
        num=len(self.connected_routers)
        for pos in range(0, num):
            r=self.connected_routers[pos]
            addr=self.ip_addresses[pos]
            if LANGUAGE==EN:
                text=text+self.name+" connected to "+r+" using "+str(addr)+"\n"
            if LANGUAGE==ES:
                text=text+self.name+" conectado con "+r+" usando la IP "+str(addr)+"\n"                
        return text
    def get_routing_table(self):
        if LANGUAGE==EN:
            print ("Routing table for "+self.name)
        if LANGUAGE==ES:
            print ("Tabla de enrutamiento para "+self.name)
        txt=""
        for route in self.routes:
            txt+=str(route) + "\n"
        return txt
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
    
class Route:
    def __init__(self, destination, via, metric):
        self.destination=destination
        self.via=via
        self.metric=metric
    #Other route can replace this route?
    def can_replace(self, route):
        same_network    =   ( self.destination ==  route.destination    )
        better_metric   =   ( self.metric      <   route.metric         )
        same_gateway    =   ( self.via         ==  route.via            )
        if same_network and better_metric and same_gateway :
            if LOGGING_ENABLED:
                print ( "{} can replace {}".format (self, route) )
            return True
        return False
    def is_better_than(self, route):
        if self.destination==route.destination and self.metric<route.metric:
                if LOGGING_ENABLED:
                    print ("{} is better than {}".format(self, route))
                return True
        if LOGGING_ENABLED:
            print ("{} isn't better than {}".format(self, route))
        return False
    def __eq__(self, route):
        if route.destination!=self.destination:
            return False
        if route.via!=self.via:
            return False
        if route.metric!=self.metric:
            return False
        return True
    def __str__(self):
        txt=""
        if LANGUAGE==EN:
            txt+="Destination {} via {} metric {}".format(self.destination, self.via, self.metric)
        if LANGUAGE==ES:
            txt+="Red de destino:{} Siguiente salto: {} metrica:{}".format(self.destination, self.via, self.metric)
        return txt
    
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



def get_metric (node1, node2):
    #metrics=networkx.get_edge_attributes(graph, 'weight')
    return int(graph[node1][node2]['weight'])

def calculate_metric(path):    
    if (len(path)==2):
        return get_metric (path[0], path[1])
    else:
        return get_metric (path[0], path[1]) + calculate_metric(path[1:])
        
    

def create_routing_table(router, graph, networks):
    
    
    for network in networks:
        paths=networkx.all_simple_paths(graph, str(router), network)
        #Paths always contains the router passed, let's remove it
        
        for path in paths:
            if (len(path)!=2):
                gateway     =   router.get_ip_to_find_router(path[1])
                destination =   network
                metric      =   calculate_metric(path)
                route       =   Route ( destination, gateway, int(metric) )
                
                router.append_route(route)
                
    
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
    
for route in routers:
    print (route.get_routing_table())
