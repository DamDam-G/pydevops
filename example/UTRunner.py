#!/usr/bin/python -O
# -*- coding: utf-8 -*-

import os
import re
from pydevops.Log import log
from pydevops.Mail import Mail

class RunUT():
    """
        This is a class for rujn unit test :
            - LaunchUT : Execute a routine about unit test, this is a static method
                * ex : RunTU.LaunchUT()
            - __CheckDiff : Check the diff between the remote repo ans the local repo
            - __Update : Update the CVS
            - __Run : Run the unit test
            - __Report : generate a report at the format txt
    """
    __UT = None

    @staticmethod
    def LaunchUT(type):
        RunUT.__UT = RunUT()
        RunUT.__UT.__Update()
        RunUT.__UT.__Run()
        RunUT.__UT.__Report(type)
        RunUT.__UT = None
        """if RunUT.__UT.__CheckDiff() == 1:
            RunUT.__UT.__Update()
            RunUT.__UT.__Run()
            RunUT.__UT.__Report(type)
            RunUT.__UT = None
        else:
            sys.exit(0)"""

    def __init__(self):
        """
            This method is the constructor of RunUT
            input parameters :
                N/A
            output :
                N/A
        """
        self.home = "/home/unittester/"
        self.moduleCVS = "slideboard-revolunet"
        self.repo = "{0}{1}/".format(self.home, self.moduleCVS)
        self.last_run = "{0}last.run".format(self.home)
        self.report = "{0}report.txt".format(self.home)
        self.jasmine = "{0}jasmine.out".format(self.home)
        self.karma = "{0}frontend/config/karma-unittester.conf.js".format(self.repo)
        os.environ["CVS_RSH"] = "ssh"
        os.environ["CVSROOT"] = ":ext:unittester@chaos:/var/lib/cvs2"
        os.environ["PATH"] = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games"
        os.environ["NODE_PATH"] = "/usr/lib/nodejs:/usr/lib/node_modules:/usr/share/javascript"

    def __CheckDiff(self):
        """
            This method check if there are differences between local and remote repo
            input parameters :
                N/A
            output :
                N/A
        """
        if os.path.exists(self.last_run):
            log(0, "last.run exist ... OK")
        else:
            os.popen("touch {0}".format(self.last_run))
            log(0, "last.run is created")
            return 1
        last = (os.popen("cat {0}".format(self.last_run)).readlines())[0].replace("\n", "")
        log(0, "Last run was at {0}".format(last))
        diff = (os.popen("cvs -q rdiff -D {0} -r HEAD {1} 2>/dev/null|wc -l".format(last, self.moduleCVS)).readlines())[0].replace("\n", "")
        print diff
        if diff != "0":
            log(0, "A diff exists ...")
            return 1
        else:
            log(0, "No diff existing ...")
            return 0

    def __Update(self):
        """
            This method try to update the cvs local repo
            input parameters :
                N/A
            output :
                N/A
        """
        os.popen("date > {0}".format(self.last_run))
        log(0, "CVS is updating")
        os.popen("cvs update -d").readlines()
        log(0, "CVS is updated")

    def __Run(self):
        """
            This method run the unit test
            input parameters :
                N/A
            output :
                N/A
        """
        os.popen("rm -rf {0}".format(self.jasmine))
        log(0, "Starting Karma Server (http://karma-runner.github.io)")
        log(0, "May the Force of the Slideboard be with you!")
        print self.karma
        print self.jasmine
        os.popen("karma start {0} $* > {1}".format(self.karma, self.jasmine))
        print "".join(os.popen("grep assertion {0}".format(self.jasmine)).readlines())
        os.popen("date '+%Y-%m-%d %H:%M' > {0}".format(self.last_run))

    def __Report(self, t):
        """
            This method generates the report
            input parameters :
                type : define if the report is at the format text or html (type = txt or html)
            output :
                N/A
        """
        log(0, "Preparing the report ...")
        os.popen("echo '' > {0}".format(self.report))
        report = os.popen("cat {0}".format(self.jasmine)).readlines()
        success = list()
        info = list()
        warn = list()
        debug = list()
        other = list()
        if t == "html":
            for i in report:
                if re.search("^INFO", i, re.IGNORECASE):
                    info.append("<tr><td>{0}</tr></td>".format(i))
                elif re.search(".*SUCCESS.*", i, re.IGNORECASE):
                    success.append("<tr><td>{0}</tr></td>".format(i))
                elif re.search("^Warn", i, re.IGNORECASE):
                    warn.append("<tr><td>{0}</tr></td>".format(i))
                elif re.search("^Debug", i, re.IGNORECASE):
                    debug.append("<tr><td>{0}</tr></td>".format(i))
                else:
                    other.append("<tr><td>{0}</tr></td>".format(i))

            jasmine = "<br />".join(os.popen("cat {0}".format(self.jasmine)).readlines())
            log(0, "The report is Writting ...")
            content = """
            <html>
                <head>
                </head>
                <body>
                    <h1 style="color:red;text-decoration:underline">Unit test report of the {0} modul</h1>
                    v
                        <tr style="font-weight:bold"><td><h2 style="text-decoration:underline">Error</h2></td></tr>
                        {1}
                    </table><br />
                    </hr>
                    <table style="background-color:#eee;padding:5px">
                        <tr style="font-weight:bold"><td><h2 style="text-decoration:underline">Warning</h2></td></tr>
                        {2}
                    </table><br />
                    <hr />
                    <table style="background-color:#eee;padding:5px">
                        <tr style="font-weight:bold"><td><h2 style="text-decoration:underline">Success</h2></td></tr>
                        {3}
                    </table><br />
                    <hr />
                    <table style="background-color:#eee;padding:5px">
                        <tr style="font-weight:bold"><td><h2 style="text-decoration:underline">Info</h2></td></tr>
                        {4}
                    </table><br />
                    <hr />
                    <table style="background-color:#eee;padding:5px">
                        <tr style="font-weight:bold"><td><h2 style="text-decoration:underline">Debug</h2></td></tr>
                        {5}
                    </table><br />
                    <hr />
                    <h2 style="text-decoration:underline">Report not parsed</h2>
                    {6}
                </body>
            </html>
            """.format(self.moduleCVS, "".join(other), "".join(warn), "".join(success), "".join(info), "".join(debug), jasmine)

        else:
            for i in report:
                if re.search("^INFO", i, re.IGNORECASE):
                    info.append("{0}".format(i))
                elif re.search(".*SUCCESS.*", i, re.IGNORECASE):
                    success.append("{0}".format(i))
                elif re.search("^Warn", i, re.IGNORECASE):
                    warn.append("{0}".format(i))
                else:
                    other.append("{0}".format(i))
            jasmine = "".join(os.popen("cat {0}".format(self.jasmine)).readlines())
            content = "Unit test report of the {0} modul\n\nError : \n\n{1}\n\n------------------------------\n\nWarning : \n\n{2}\n\n------------------------------\n\nSuccess : \n\n{3}\n\n------------------------------\n\nInfo :\n\n{4}\n\n------------------------------\n\nInfo :\n\n{5}\n\n------------------------------\n\nFull Report not parsed : \n\n{6}".format(self.moduleCVS, "\n".join(other), "\n".join(warn), "\n".join(success), "\n".join(info), "\n".join(debug), jasmine)
        log(0, "The report is Wrote")
        fd = open(self.report, "a")
        fd.write(content)
        fd.close()
        log(0, "The report is finished")

if __name__ == '__main__':
        RunUT.LaunchUT("html")
        Mail.Email({"from":"unittester@one2team.com",
                    "to":"lmn@one2team.com",
                    "subject":"Report Unit test",
                    "text":" ".join(os.popen("cat /home/unittester/report.txt").readlines()),
                    "srv":"apache1.admin.one2team.rod",
                    "type":"html"})
        Mail.Email({"from":"unittester@one2team.com",
                    "to":"dgg@one2team.com",
                    "subject":"Report Unit test",
                    "text":" ".join(os.popen("cat /home/unittester/report.txt").readlines()),
                    "srv":"apache1.admin.one2team.rod",
                    "type":"html"})