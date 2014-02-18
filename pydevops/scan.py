from scapy.all import *
import socket
import re
import os
import json


class Scan:
    """
    Class in development
    """
    def __init__(self, mask):
        """
        """
        self.net = []
        #self.interface = interface
        self.mask = mask
        self.gw = ''
        self.mac = ''
        self.route = []
        self.device = 'router'
        self.mac_constructor = (os.popen("grep -e \"base 16\" -R mac_constructor")).readlines()

    def GetIpMac(self):
        """
        """
        n = list()
        cmd = list()
        ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=self.mask), timeout=2)
        ans.summary(lambda (s, r): cmd.append(r.sprintf("%Ether.src% %ARP.psrc%").split(" ")))
        [n.append({"mac": i[0], "ip": i[1], "device": self.GetDevice(i[0]), "os": None, "hostname": self.GetHostName(i[1])}) for i in cmd]
        self.net = n

    def GetHostName(self, ip):
        """
        """
        return socket.getfqdn(ip)

    def GetGW(self):
        """
        """
        self.gw = list(set(((os.popen('route -n | grep -e "0\.0\.0\.0 *[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\} *0\.0\.0\.0"')).read()).split(" ")))[1]

    def GetDevice(self, mac):
        """
        """
        for line in self.mac_constructor:
            if re.search(("".join((mac.split(':', 3))[0:3])).upper(), line):
                r = line.split("\t")
                r.reverse()
                for k, v in {"nokia":"phone", "ericsson":"phone", "samsung":"phone", "apple":"apple", "vmware":"vm"}.items():
                    if re.search(k, r[0].lower().replace("\n", "")):
                        return v
                break
        return "computer"

    def GetOS(self, ip):
        """
        """
        pass

    def GetNetwork(self, opt):
        """
        """
        n = {'gw':self.gw, 'route':self.route, 'net':self.net}
        if opt == 0:
            return n
        elif opt == 1:
            return json.dumps(n)
        else:
            print("[ERROR] GetNetwork(self, opt) : opt must equal 0 (dict) or 1 (json)")

if __name__ == "__main__":
    s = Scan("172.18.0.0/24")
    #print s.GetDevice2("b8:ac:6f:43:39:cd")
    print s.GetDevice2("00:50:56:93:10:DC")
    """s = Scan("172.18.0.0/24")
    s.GetGW()
    s.GetIpMac()
    print s.GetNetwork(0)
    print "-"*20
    print s.GetNetwork(1)"""
