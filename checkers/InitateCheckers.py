from checkers.LinuxFileChecker import *
from checkers.PingVM import *


def runchecker(checkertype, checkertask, checkercondition, machine):
    if checkertype == "ping":
        if checkertask == "icmpping":
            result = icmpping(machine)
        elif checkertask == "portcheck":
            result = portcheck(machine, checkercondition)
        print("WIP")
    else:
        print("Checker not available")

    return result


