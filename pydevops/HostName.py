from scapy.all import *
import socket
import re

def getAllHostnameWithFilter(netmask, filter):
    t = list()
    server = list()
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=netmask), timeout=2)
    ans.summary(lambda (s, r): t.append(r.sprintf("%Ether.src% %ARP.psrc%")))
    for i in t:
        r = socket.getfqdn((i.split(" "))[1])
        if re.search(filter, r):
            server.append(r)
    return server

def getAllWithFilter(netmask, filter):
    t = list()
    server = list()
    ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=netmask), timeout=2)
    ans.summary(lambda (s, r): t.append(r.sprintf("%Ether.src% %ARP.psrc%")))
    for i in t:
        r = socket.getfqdn((i.split(" "))[1])
        if re.search(filter, r):
            server.append({"hostname":r, "ip":(i.split(" "))[1]})
    return server

if __name__ == "__main__":
    servers1 = list()
    other = list()
    r = getAllHostnameWithFilter("10.40.0.0/16", "^(toto|titi|tata|tutu)\.riri\.com\.*$")
    [servers1.append(i) if re.search("^toto", i) else other.append(i) for i in r]
    print """\n""".join(servers1)
    print "\n____________________________________________________\n\n"
    print """\n""".join(other)