from checkers.LinuxFileChecker import *
from checkers.PingVM import *


def runchecker(checkertype, checkertask, checkercondition, machine, options):
    if checkertype == "ping":
        if checkertask == "icmpping":
            result = icmpping(machine, checkercondition)
            print(f"result for icmpping is {result}")
        elif checkertask == "portcheck":
            result = portcheck(machine, checkercondition, options)
        else:
            print(f"Ping Checker {checkertask} does not exist.")

    # Initiate your checkers here. Please note they can only return True or False

    else:
        print("Checker not available")

    return result


