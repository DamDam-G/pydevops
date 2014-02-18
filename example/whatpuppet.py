#!/usr/bin/python -O
# -*- coding: utf-8 -*-

from pydevops.SSH import SSH
from pydevops.Mail import *
from pydevops import HostName

target = list()
[target.append([{"hostname":i, "user":"root", "pwd":""}, ["yum info puppet", "puppet agent  --no-daemonize --onetime --verbose --show_diff --color=false --noop"], i]) for i in HostName.getAllWithFilter("10.40.0.0/16", "^(toto|titi|tata|tutu)\.riri\.com\.*$")]

r = SSH.ParallaxExec(target)

rapport = "<html><head></head><body>"
for i in r:
    rapport += '<h1 style="color:red;text-decoration:underline">{0}</h1><div style="color:#000000;background-color:#eee;padding:5px">{1}</div><br />'.format(i["server"], ("""""".join(i["result"]["rcmd"]).replace("\n", '<br />')))

rapport += "</body></html>"

Mail.Email({"from":"puppet@one2team.com",
                    "to":"dgg@one2team.com",
                    "subject":"Rapport puppet migration 2.6 to 3.3",
                    "text":rapport,
                    "srv":"apache1.admin.one2team.rod",
                    "type":"html"})