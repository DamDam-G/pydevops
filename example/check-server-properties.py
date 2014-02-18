#!/usr/bin/python -O
from pydevops.SSH import SSH
from pydevops import HostName


if __name__ == "__main__":
        cmd = ['grep "cache.memcached.server.host"  /var/lib/tomcat5/webapps/one2team/WEB-INF/classes/sso.properties']
        params = list()
        for i in HostName.getAllWithFilter("10.40.0.0/16", "^(toto|titi|tata|tutu)\.riri\.com\.*$"):
           params.append([{"hostname":i.replace("\n", ""), "user":'root', "pwd":""}, cmd, i.replace("\n", "")])

        r = SSH.ParallaxExec2(params)
        print r
        for i in r:
            print i["server"]+" => "+"".join(i["result"])