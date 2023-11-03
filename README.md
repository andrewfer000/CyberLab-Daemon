# CyberLab-Daemon
CyberLab Daemon is the software that controls QEMU/KVM and Apache Guacamole

## What is the CyberLab Daemon for?
Cyberlab is split into two parts. The frontend, where users log in, launch labs, and track progress. The Daemon, which is what manages Apache Guacamole, QEMU/KVM, Sessions, and is where your courses reside. 
You can have multiple daemons with different courses to help balance load. More will be comming soon. 

## How do I use this?
Simialr to the concept version, You need to create a Virtual Environment and install the same requirements as the concept AS WELL AS flask. I develop on Fedora 38 so the latest versions will do. The "app.py" MUST run on a Linux host with Apache Guacamole with MySQL authentication setup and QEMU/KVM

1. Download the files from git, place it somewhere nice, Edit the config.json to reflect your Guacamole admin credentals. Libvirt credentails are currently not used so ensure you are running the app as a user who can interact with libvirt. if everything is installed then the app should start in debug mode if you run "app.py". You can use a WSGI server like Gunicorn to run it in a more production-like enviornment. However, security and the frontend is not prepared yet so this is not ready for production.
2. 
