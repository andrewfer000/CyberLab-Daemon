import subprocess
import socket

def portcheck(hostname, port=80, timeout=2):
    try:
        with socket.create_connection((hostname, port), timeout=timeout):
            return True
    except (socket.timeout, socket.error):
        return False

def icmpping(hostname):
    try:
        subprocess.check_output(["ping", "-c", "2", "-W", "2", hostname])
        return True
    except subprocess.CalledProcessError:
        return False
