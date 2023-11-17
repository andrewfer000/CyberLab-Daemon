# CyberLab-Daemon
CyberLab Daemon is the software that controls QEMU/KVM and Apache Guacamole

## What is the CyberLab Daemon for?
Cyberlab is split into two parts. The frontend, where users log in, launch labs, and track progress. The Daemon, which is what manages Apache Guacamole, QEMU/KVM, Sessions, and is where your courses reside. 
You can have multiple daemons with different courses to help balance load. More will be comming soon. 

## How do I use this?
Simialr to the concept version, You need to create a Virtual Environment and install the same requirements as the concept AS WELL AS flask. I develop on Fedora 38 so the latest versions will do. The "app.py" MUST run on a Linux host with Apache Guacamole with MySQL authentication setup and QEMU/KVM

1. Download the files from git, place it somewhere nice, Edit the config.json to reflect your Guacamole admin credentals. Libvirt credentails are currently not used so ensure you are running the app as a user who can interact with libvirt. if everything is installed then run the `gunicorn.py` file to start the software.
2. `cyberlab_cli.py` is the command line tool. It works similar to the concept version of the software. You can run this on any host as long as it can reach the daemon. Be sure to configure the daemon.json file with the correct URL and connection key. 
3. If you have a course with a lab ready, then you can run `cyberlab_cli.py --demosession testcourse/testlab` This command will send the API requests to create a new session, build the session (VM, Networks, Guac Config), and then build the lab. It will then generate the HTML page to access the lab. Please note all URLs generated will be based on the daemon's config.json so if you're using a remote device with a reverse proxy please reflect that in your config.json
4. When you're done. Run `cyberlab_cli.py --destorysession 'session_id'` to end destory the guacamole user, connections, VM(s), VM Disk(s), and VM network(s).


https://github.com/andrewfer000/CyberLab
