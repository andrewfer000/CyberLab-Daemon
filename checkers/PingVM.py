import subprocess
import socket

def portcheck(hostname, checkercondition, options):
    try:
        port = options[0]
        timeout = options[1]
        with socket.create_connection((hostname, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False

    if checkercondition == "offline" and Pings == False:
        return True
    elif checkercondition == "online" and Pings == True:
        return True
    elif checkercondition == "offline" and Pings == True:
        return False
    elif checkercondition == "online" and Pings == False:
        return False
    else:
        return False


def icmpping(hostname, checkercondition):
    Pings = False
    try:
        subprocess.check_output(["ping", "-c", "2", "-W", "2", hostname])
        Pings = True
    except subprocess.CalledProcessError:
        Pings = False

    print(Pings)
    if checkercondition == "offline" and Pings == False:
        return True
    elif checkercondition == "online" and Pings == True:
        return True
    elif checkercondition == "offline" and Pings == True:
        return False
    elif checkercondition == "online" and Pings == False:
        return False
    else:
        return False
