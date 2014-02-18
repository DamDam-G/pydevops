#!/usr/bin/python -O
# -*- coding: utf-8 -*-
import sys
import smtplib
from email.MIMEText import MIMEText
from Log import *

class Mail():
    """
        This is a class for sending mail with smtp :
            - Email : Execute a routine about macil, this is a static method
                * ex : Mail.Email({"from":"dgg@one2team.com", "to":"dgg@one2team.com", "subject":"Report Unit test", "text":" ".join(os.popen("cat /home/unittester/report.txt").readlines()), "srv":"apache1.admin.one2team.rod", "type":"txt"})
            - __Send : Send an email
            - __Close : Close the session with the server mail
    """
    __email = None

    @staticmethod
    def Email(obj):
        try:
            Mail.__email = Mail(obj["from"], obj["to"], obj["subject"], obj["text"], obj["srv"], obj["type"])
            log(0, "Sending the email ...")
        except KeyError:
            log(1, "One of parameters is missing or false")
            sys.exit(1)
        else:
            Mail.__email.__Send()
            log(0, "The email is sent")
            Mail.__email.__Close()
            Mail.__email = None

    def __init__(self, mfrom, mto, subject, text, srv, type):
        """
            This method is the constructor of Mail
            input parameters :
                - obj : this is an object who contains : (dict)
                    - from : the address src (str)
                    - to : the address dest (str)
                    - subject : the subject of the email  (str)
                    - text : the content of the email (str)
                    - srv : the address of the server smtp (str)
                    - type : the type of the email (html or text)  (str)
            output :
                Mail Object
        """
        self.mfrom = mfrom
        self.mto = mto
        self.subject = subject
        self.text = text
        self.srv = srv
        self.email = MIMEText(text, 'plain') if type == "txt" else MIMEText(text, 'html')
        self.email['From'] = mfrom
        self.email['To'] = mto
        self.email['Subject'] = subject
        self.server = smtplib.SMTP(srv)

    def __Send(self):
        """
            This method send email
            input parameters :
                N/A
            output :
                N/A
        """
        self.server.sendmail(self.mfrom, self.mto, self.email.as_string())

    def __Close(self):
        """
            This method close session smtp
            input parameters :
                N/A
            output :
                N/A
        """
        self.server.quit()