#!/usr/bin/python -O

import socket
import paramiko
import select
import sys
import os
import signal
from Log import *

__author__ = "Damien Goldenberg - dgg"
__version__ = "0.1"

class SSH():
    """
        This is a class for ssh connection who can :
            - Exec : Execute a routine about ssh session, this is a static method
                * ex : SSH.ExecAll({"hostname":'google.com', "user":'root', "pwd":"xxxxxx", "cmd":["ls -la", "pwd", "ps aux", "whoami", "echo 1"]}))
                * SigHandler : this is a handler to interrupt the routine
            - __Connect : Connect to a server
            - __Exec : Execute and return the stdout
            - __Disconnect : Disconnect of the server
            - __Kill : Kill the actual remote command
    """

    __current_client = None
    __parallax_clients = {"inckill":0, "clients":{}}

    @staticmethod
    def Exec(obj, cmd):
        """
        This function is a static method. It uses to execute a routine about a ssh session
        This method does :
            1) Connect to the server
            2) Execute a list of command
            3) Disconnect of the server
            There is a handler to interrupt the routine on the signal SIGINT
        input parameters :
            - obj : this is an object who contains : (dict)
                    - hostname : the address of the server to connect (str)
                    - user : the user who connects on the server (str)
                    - pwd : the user's password it's optional, it can use rsa key (str)
            - cmd : a list of commands to execute (list)
        output :

        """
        def SigHandler(signal, frame):
            """
            This function is an handler for gets back a signal system
            input parameters :
                - signal : this is the type of signal (int)
                - frame : this is the name of the handler function (name function)
            output :
                    N/A
            """
            if signal == 2 and SSH.__current_client is not None:
                log(0, "The signal SIGINT is getting back")
                SSH.__current_client.__Kill()
        r = None
        SSH.__current_client = SSH(obj)
        signal.signal(signal.SIGINT, SigHandler)
        SSH.__current_client.__Connect()
        #r = SSH.__current_client.__Exec(cmd)
        r = SSH.__current_client.__Exec2(cmd)
        SSH.__current_client.__Disconnect()
        SSH.__current_client = None
        return r

    @staticmethod
    def ParallaxExec(objs):
        """
        This function is a static method. It uses to execute a routine about a ssh session
        This method does :
            1) Connect to the server
            2) Execute a list of command
            3) Disconnect of the server
            There is a handler to interrupt the routine on the signal SIGINT
        input parameters :
            - obj : this is an object who contains : (dict)
                    - hostname : the address of the server to connect (str)
                    - user : the user who connects on the server (str)
                    - pwd : the user's password it's optional, it can use rsa key (str)
            - cmd : a list of commands to execute (list)
        output :

        """
        from multiprocessing import Process, Queue, TimeoutError

        def MyThread(queue, obj, cmd, name):
            def TheSigHandler(frame, signal):
                if SSH.__parallax_clients["clients"][name] is not None:
                    print "The kill is incomming on {0}".format(name)
                    SSH.__parallax_clients["clients"][name].__Kill()
                    SSH.__parallax_clients["clients"][name] = None

            r = None
            SSH.__parallax_clients["clients"][name] = SSH(obj, queue)
            print SSH.__parallax_clients
            signal.signal(signal.SIGINT, TheSigHandler)
            SSH.__parallax_clients["clients"][name].__Connect()
            r = SSH.__parallax_clients["clients"][name].__Exec(cmd)
            SSH.__parallax_clients["clients"][name].__Disconnect()
            del SSH.__parallax_clients["clients"][name]
            queue.put(r)

        def SigHandler2(signal, frame):
            """
            This function is an handler for gets back a signal system
            input parameters :
                - signal : this is the type of signal (int)
                - frame : this is the name of the handler function (name function)
            output :
                    N/A
            """
            if signal == 2 and SSH.__parallax_clients["inckill"] == 0:
                SSH.__parallax_clients["inckill"] = 1
                log(0, "The signal SIGINT is getting back")
                #print threads
                for i in threads:
                    os.popen("skill -INT {0}".format(i["worker"].pid))
                    print "pass"
                    #i["worker"].join()
                    #del i
                sys.exit(0)

        threads = list()
        res = list()
        signal.signal(signal.SIGINT, SigHandler2)
        for i in objs:
            q = Queue()
            threads.append({"name":i[2], "pipe":q, "worker":Process(target=MyThread, args=(q, i[0], i[1], i[2],))})
        for i in threads:
            i["worker"].start()
        for i in threads:
            i["worker"].join()
        for i in threads:
            res.append({"server": i["name"], "result": i["pipe"].get()})
        return res

    @staticmethod
    def ParallaxExec2(objs):
        """
        This function is a static method. It uses to execute a routine about a ssh session
        This method does :
            1) Connect to the server
            2) Execute a list of command
            3) Disconnect of the server
            There is a handler to interrupt the routine on the signal SIGINT
        input parameters :
            - obj : this is an object who contains : (dict)
                    - hostname : the address of the server to connect (str)
                    - user : the user who connects on the server (str)
                    - pwd : the user's password it's optional, it can use rsa key (str)
            - cmd : a list of commands to execute (list)
        output :

        """
        from multiprocessing import Process, Queue, TimeoutError

        def MyThread(queue, obj, cmd, name):
            def TheSigHandler(frame, signal):
                if SSH.__parallax_clients[name] is not None:
                    print "The kill is incomming on {0}".format(name)
                    SSH.__parallax_clients[name].__Kill()
                    SSH.__parallax_clients[name] = None

            r = None
            SSH.__parallax_clients[name] = SSH(obj, queue)
            signal.signal(signal.SIGINT, TheSigHandler)
            SSH.__parallax_clients[name].__Connect()
            r = SSH.__parallax_clients[name].__Exec2(cmd)
            SSH.__parallax_clients[name].__Disconnect()
            del SSH.__parallax_clients[name]
            queue.put(r)

        def SigHandler2(signal, frame):
            """
            This function is an handler for gets back a signal system
            input parameters :
                - signal : this is the type of signal (int)
                - frame : this is the name of the handler function (name function)
            output :
                    N/A
            """
            if signal == 2:
                log(0, "The signal SIGINT is getting back")
                print threads
                for i in threads:
                    os.popen("skill -INT {0}".format(i["worker"].pid))
                    #i["worker"].join()
                    #del i
                sys.exit(0)

        threads = list()
        res = list()
        signal.signal(signal.SIGINT, SigHandler2)
        print len(objs)
        for i in objs:
            q = Queue()
            print i
            threads.append({"name":i[2], "pipe":q, "worker":Process(target=MyThread, args=(q, i[0], i[1], i[2],))})
        for i in threads:
            i["worker"].start()
        for i in threads:
            i["worker"].join()
        for i in threads:
            res.append({"server": i["name"], "result": i["pipe"].get()})
        return res

    def __init__(self, obj, queue=None):
        """
            This method is the constructor of SSH
            input parameters :
                - obj : this is an object who contains : (dict)
                    - hostname : the address of the server to connect (str)
                    - user : the user who connects on the server (str)
                    - pwd : the user's password (str)
            output :
                N/A
        """
        try:
            self.hostname = obj["hostname"]
            self.user = obj["user"]
            self.pwd = obj["pwd"]
            self.pgid = None
        except KeyError:
            log(1, self.__init__.__doc__)
            sys.exit(1)

        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.queue = queue
        self.getsigkill = 0

    def __Connect(self):
        """
            this method try to connect on a server
            input parameters :
                N/A
            output :
                N/A
        """
        try:
            log(0, "ssh connection in progress to {0}".format(self.hostname))
            self.ssh.connect(self.hostname, username=self.user, password=self.pwd)
        except socket.gaierror:
            log(1, "Host unknown : {0}".format(self.hostname))
            self.__CheckQueue("The SSH connection failed, please check your param")
            sys.exit(1)
        except paramiko.SSHException:
            log(1, "Unknown server {0} or error on the connection or establishing an SSH session".format(self.hostname))
            self.__CheckQueue("The SSH connection failed, please check your param")
            sys.exit(1)
        except paramiko.BadHostKeyException:
            log(1, "the server's host key could not be verified")
            self.__CheckQueue("The SSH connection failed, please check your param")
            sys.exit(1)
        except paramiko.AuthenticationException:
            log(1, "authentication failed")
            self.__CheckQueue("The SSH connection failed, please check your param")
            sys.exit(1)
        except socket.error:
            log(1, "socket error occurred while connecting")
            self.__CheckQueue("The SSH connection failed, please check your param")
            sys.exit(1)
        else:
            log(0, "ssh connection established on {0}".format(self.hostname))

    def __CheckQueue(self, msg):
        if self.queue is not None:
                self.queue.put(msg)

    def __Exec(self, cmd):
        """
            This method try to exec a list of commands and to register the ssh ppid
            input parameters :
                - cmd : this is commands to execute (list)
            output :
                - rcmd : this is the stdout of the list of command (list)
        """
        rcmd = list()
        transport = self.ssh.get_transport()
        channel = transport.open_session()
        try:
            """
                it's to get back the pid of the session ssh, $$ represents the pid of bash in the session ssh
            """
            stdin, stdout, stderr = self.ssh.exec_command("ps -p $$ -o pgid=")
            self.pgid = stdout.read().replace("\n", "")
            log(0, " [SERVER] {0} - get back the actual pgid {1}".format(self.hostname, self.pid))
        except paramiko.SSHException:
            log(1, "< {0} > the server fails to get the pgid of the command ps -p $$ -o pgid=".format(self.hostname))
            self.__Disconnect()
            sys.exit(1)
        try:
            """
            TODO explain the hack
            Here we check if the param cmd is different of None, to choice the good commands list to execute.
            After, we concatenate the list in a docstring with "\n" for execute all commands to avoid a loop and don't create a new session for each command
            """
            channel.exec_command("""\n""".join(cmd))
            log(0, " [SERVER] {0} - {1} {2} running".format(self.hostname, " ; ".join(cmd), "is" if len(cmd) == 1 else "are"))
        except paramiko.SSHException:
            log(1, "< {0} > the server fails to execute {1}".format(self.hostname, cmd))
            self.__Disconnect()
            sys.exit(1)
        else:
            while True:
                if channel.exit_status_ready():
                    log(0, " [SERVER] {0} - {1} {2} executed ".format(self.hostname, " ; ".join(cmd), "was" if len(cmd) == 1 else "were"))
                    channel.close()
                    return {"rc":0 if channel.exit_status == 0 else 1, "rcmd":rcmd}
                rl, wl, xl = select.select([channel], [], [], 0.0)
                if len(rl) > 0:
                    print channel.recv(1024)
                    rcmd.append(channel.recv(1024))

    def __Exec2(self, cmd):
        rcmd = list()
        stdin, stdout, stderr = self.ssh.exec_command("".join(cmd))
        for line in stdout.readlines():
            print line
            rcmd.append(line)
        return rcmd

    def __Kill(self):
        """
        this method kill the actual remote command
        input parameters :
                N/A
        output :
                N/A
        """
        if self.getsigkill == 0:
            self.getsigkill = 1
            try:
                self.ssh.exec_command("kill -9 {0}".format(self.pgid))
                log(0, "< {0} > the session ssh (pid :{1}) was killed".format(self.hostname, self.pgid))
            except paramiko.SSHException:
                log(1, "< {0} > the server failed to kill the session ssh (pgid :{1})".format(self.hostname,  self.pgid))
                self.__Disconnect()
                self.__CheckQueue("the build tries to stop")
                sys.exit(1)
            except AttributeError:
                log(1, "< {0} > the server failed to kill the session ssh (pgid :{1})".format(self.hostname,  self.pgid))
                self.__Disconnect()
                self.__CheckQueue("the build tries to stop")
                sys.exit(1)
            else:
                self.__Disconnect()
                self.__CheckQueue("the build tries to stop")
                log(0, "the build is stopping now")
                """
                    why exit 1? Because we would show a fail on the jenkins dashboard, if it's 0 the jenkins build says it's sucessfull
                """
                sys.exit(1)
        else:
            sys.exit(1)

    def __Disconnect(self):
        """
        This method disconnect the current session ssh
        input parameters :
                N/A
        output :
                N/A
        """
        self.ssh.close()
        log(0, " [SERVER] {0} - ssh connection closed".format(self.hostname))

class SFTP():
    """
        This is a class for sftp connection who can :
            - Files : Execute a routine about sftp session, this is a static method
                * ex : SFTP.Files({"hostname":'google.com', "user":'root', private_key:"/home/super_zozor/.ssh/id_rsa", "directory":"/tmp/getback", "action":"GET"})
            - __Connect : Connect to a server
            - __GetBack : get back some files of the remote dir to the local dir
            - __PutOn : not available
            - __Disconnect : Disconnect of the server
    """

    __current_files = None
    __current_files2 = {}

    @staticmethod
    def Files(obj):
        """
        This function is a static method. It uses to execute a routine about a sftp session
        This method does :
            1) Connect to the server
            2) Get back / Put on some files
            3) Disconnect of the server
        input parameters :
            - obj : this is an object who contains : (dict)
                    - hostname : the address of the server to connect (str)
                    - user : the user who connects on the server (str)
                    - port : the port to access to the server by default 22 (can be equal None or "")(str)
                    - private_key : this is the path to .ssh/id_rsa (str)
                    - dir : this is the remote and local dir, Ldirectory = local directory, Rdirectory = remote directory
                    - action : this is the action to do, it can only be only equal to "GET" or "PUT"
        output :

        """
        SFTP.__current_files = SFTP(obj)
        SFTP.__current_files.__Connect()
        try:
            assert obj["action"] == "GET" or obj["action"] == "PUT"
            SFTP.__current_files.__GetBack() if obj["action"] is "GET" else SFTP.__current_files.__PutOn()
        except KeyError:
            log(1, "The parameter action is not indicated")
            log(1, SFTP.Files.__doc__)
        except AssertionError:
            log(1, "The parameter action must be equal to GET or PUT")
        finally:
            SFTP.__current_files.__Disconnect()
            SFTP.__current_files = None
            return None

    @staticmethod
    def Files2(obj, name):
        """
        This function is a static method. It uses to execute a routine about a sftp session
        This method does :
            1) Connect to the server
            2) Get back / Put on some files
            3) Disconnect of the server
        input parameters :
            - obj : this is an object who contains : (dict)
                    - hostname : the address of the server to connect (str)
                    - user : the user who connects on the server (str)
                    - port : the port to access to the server by default 22 (can be equal None or "")(str)
                    - private_key : this is the path to .ssh/id_rsa (str)
                    - dir : this is the remote and local dir, Ldirectory = local directory, Rdirectory = remote directory
                    - action : this is the action to do, it can only be only equal to "GET" or "PUT"
        output :

        """
        SFTP.__current_files2[name] = SFTP(obj)
        SFTP.__current_files2[name].__Connect()
        try:
            assert obj["action"] == "GET" or obj["action"] == "PUT"
            SFTP.__current_files2[name].__GetBack() if obj["action"] is "GET" else SFTP.__current_files2[name].__PutOn()
        except KeyError:
            log(1, "The parameter action is not indicated")
            log(1, SFTP.Files2.__doc__)
        except AssertionError:
            log(1, "The parameter action must be equal to GET or PUT")
        finally:
            SFTP.__current_files2[name].__Disconnect()
            del SFTP.__current_files2[name]
            return None


    def __init__(self, obj):
        """
            This method is the constructor of SFTP
            input parameters :
                - obj : this is an object who contains : (dict)
                    - hostname : the address of the server to connect (str)
                    - user : the user who connects on the server (str)
                    - port : the port to access to the server by default 22 (can be equal None or "")(str)
                    - private_key : this is the path to .ssh/id_rsa (str)
                    - dir : this is the remote and local dir, Ldirectory = local directory, Rdirectory = remote directory
            output :
                N/A
        """
        try:
            self.hostname = obj["hostname"]
            self.port = 22 if obj["port"] is None or obj["port"] == "" else obj["port"]
            self.user = obj["user"]
            self.private_key = obj["private_key"]
            try:
                self.pwd = obj["pwd"]
            except KeyError:
                self.pwd = ""
            self.dir = {"local":obj["Ldirectory"], "remote":obj["Rdirectory"]}
        except KeyError:
            log(1, self.__init__.__doc__)
            sys.exit(1)
        self.transport = paramiko.Transport((self.hostname, self.port))
        self.sftp = None

    def __Connect(self):
        """
            this method try to connect on a server
            input parameters :
                N/A
            output :
                N/A
        """
        log(0, "sftp connection in progress to {0}".format(self.hostname))
        try:
            #self.transport.connect(username=self.user, password="devel", pkey=paramiko.RSAKey.from_private_key(os.popen("cat {0}".format(self.private_key))))
            if self.pwd is not "":
                self.transport.connect(username=self.user, password=self.pwd)
            else:
                self.transport.connect(username=self.user, pkey=paramiko.RSAKey.from_private_key(os.popen("cat {0}".format(self.private_key))))
        except paramiko.SSHException:
            log(1, "Unknown server {0} or logins invalid or host key is incorrect".format(self.hostname))
            sys.exit(1)
        else:
            log(0, "sftp connection established on {0}".format(self.hostname))
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def __GetBack(self):
        """
            This method try to get back all files in the remote dir to the local dir
            input parameters :
                - N/A
            output :
                N/A
        """
        log(0, "The get back is beginning")
        ldir = self.sftp.listdir(self.dir["remote"])
        for i in ldir:
            try:
                self.sftp.get(remotepath="{0}/{1}".format(self.dir["remote"], i), localpath="{0}/{1}".format(self.dir["local"], i))
                log(0, "[SERVER] {0} - GetBack of {1}".format(self.hostname, i))
            except IOError:
                log(1, "[SERVER] {0} - File ({1}) not found or a problem is encountered with this one or the remote or local directory is missing or have a problem".format(self.hostname, i))
                self.__Disconnect()
                sys.exit(1)

    def __PutOn(self):
        """
        This method try to put on something to a server
        """
        log(0, "The ... is beginning")
        ldir = os.popen("ls {0}".format(self.dir["local"])).readlines()
        for i in ldir:
            try:
                i = i.replace("\n", "")
                self.sftp.put(localpath="{0}/{1}".format(self.dir["local"], i), remotepath="{0}/{1}".format(self.dir["remote"], i))
                log(0, "[SERVER] {0} - Put on {1}".format(self.hostname, i))
            except IOError:
                log(1, "[SERVER] {0} - File ({1}) not found or a problem is encountered with this one or the remote or local directory is missing or have a problem".format(self.hostname, i))
                self.__Disconnect()
                sys.exit(1)

    def __Disconnect(self):
        """
        This method disconnect the current session sftp
        input parameters :
                N/A
        output :
                N/A
        """
        self.sftp.close()
        log(0, "[SERVER] {0} - sftp connection closed".format(self.hostname))
        self.transport.close()