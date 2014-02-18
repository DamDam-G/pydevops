#!/usr/bin/python -O
from pydevops.SSH import *

class Puppet3():

    __current_update = None

    @staticmethod
    def Puppet3Updater(obj):
        Puppet3.__current_update = Puppet3(obj["deploy"], obj["rh5Servers"], obj["rh6Servers"])
        Puppet3.__current_update.__UploadReposFile()
        Puppet3.__current_update.__ConfDeploy()
        Puppet3.__current_update.__UpdateInfra()

    def __init__(self, deploy, rh5Servers, rh6Servers):
        self.user = "root"
        self.directory = "/root/puppet3/"
        self.servers = {
            "deploy":{"ldir":"{0}deploy/".format(self.directory), "servers":deploy},
            "rh5":{"ldir":"{0}rh5/".format(self.directory), "servers":rh5Servers},
            "rh6":{"ldir":"{0}rh6/".format(self.directory), "servers":rh6Servers}
        }

    def __UploadReposFile(self):
        for k, v in self.servers.items():
            for i in v["servers"]:
                SFTP.Files({
                        "hostname":"{0}".format(i["hostname"]),
                        "user":self.user,
                        "pwd":i["pwd"],
                        "private_key":"",
                        "port":"",
                        "Ldirectory" :v["ldir"],
                        "Rdirectory":"/etc/yum.repos.d/",
                        "action":"PUT"
                })

    def __ConfDeploy(self):
        cmd = ["mkdir -p /var/ftp/rh5/puppet/",
               "mkdir -p /var/ftp/rh6/puppet/",
               "scp -o 'StrictHostKeyChecking no' -r root@origin-rpm-puppet3.admin.one2team.rod:{0}puppet-rpm/rh6/* /var/ftp/rh6/puppet/".format(self.directory),
               "scp -o 'StrictHostKeyChecking no' -r root@origin-rpm-puppet3.admin.one2team.rod:{0}puppet-rpm/rh5/* /var/ftp/rh5/puppet/".format(self.directory),
               "createrepo -s sha /var/ftp/rh5/puppet/puppetlabs-deps-5/",
               "createrepo -s sha /var/ftp/rh5/puppet/puppetlabs-products-5/",
               "createrepo -s sha /var/ftp/rh6/puppet/puppetlabs-deps-6/",
               "createrepo -s sha /var/ftp/rh6/puppet/puppetlabs-products-6/",
               "service puppetmaster stop",
               "yum install -y puppet",
               "service puppetmaster start"]
        SSH.ParallaxExec([({"hostname":"{0}.admin.one2team.rod".format(self.servers["deploy"]["servers"][0]["hostname"]), "user":self.user, "pwd":self.servers["deploy"]["servers"][0]["pwd"]},
                           cmd,
                           self.servers["deploy"]["servers"][0]["hostname"])])

    def __UpdateInfra(self):
        cmd = ["yum remove -y ruby", "yum install -y ruby", "yum install -y puppet", "mv -f /etc/puppet/puppet.conf.rpmsave /etc/puppet/puppet.conf"]
        obj = []
        for k, v in self.servers.items():
            if k is "deploy":
                pass
            else:
                for i in v["servers"]:
                    obj.append((
                        {"hostname":"{0}".format(i["hostname"]), "user":self.user, "pwd":i["pwd"]},
                        cmd,
                        i["hostname"]
                    ))
        SSH.ParallaxExec(obj)
