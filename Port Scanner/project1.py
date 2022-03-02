#!/usr/bin/python3

# Husam Almanakly - ECE303 Comm Nets Project 1

import sys, getopt, socket
from unittest import result

#Parse command line input
try:
    hostname = "google.com"                      #Default hostname
    argv = sys.argv
    portRange = [1,1024]                         #Default Port Range
    opts, args = getopt.gnu_getopt(argv, "p:") 
except:
    print("Usage: ./project1.py hostname <-p 15:25>")
    sys.exit(2)

#Extract port range specified (if given)
if len(opts) != 0:
    portRange = opts[0][1].split(":")
    portRange = list(map(int, portRange))

#Get the hostname (if given)
if len(args) > 1: 
    hostname = args[1]

for i in range(portRange[0], portRange[1]+1):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.settimeout(0.1)
    result = s.connect_ex((hostname, i))
    if (result == 0):
        print(f"Port number {i} is open")
        try:
            serviceName = socket.getservbyport(i, "tcp");
            print(f"Default Protocol: {serviceName}")
        except: 
            continue
    else:
        continue
        # print(f"Port number {i} is not open")






