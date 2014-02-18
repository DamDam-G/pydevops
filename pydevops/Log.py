#!/usr/bin/python -O

def log(type, msg):
    """
    This function prints log
    type : define the type of the log (info (0)/error (1)) (int)
    msg : define the message to display (str)
    """
    print "[{0}] {1}".format(("INFO" if type == 0 else "ERROR"), msg)