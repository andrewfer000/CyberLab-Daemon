import json, random, string, os, argparse, shutil, psutil
from jinja2 import Environment, FileSystemLoader, Template
from datetime import datetime
from functions.libvirt_automated import *
from functions.guacamole_auto_configure import *
from functions.misc_functions import *
from functions.xml_generator import *
from functions.get_client_urls import get_client_url
from functions.generate_lab import GenerateLab
from flask import Flask, render_template, request, jsonify
from checkers.InitateCheckers import *

app = Flask(__name__)
def getvars():
    with open('config.json', 'r') as file:
        config = json.load(file)

    GUAC_SECURITY = config['connections']['Local']['Guacamole']['Security']
    GUACAMOLE_URL = config['connections']['Local']['Guacamole']['URL']
    GUAC_FULL_URL = f"{GUAC_SECURITY}://{GUACAMOLE_URL}"
    GUACAMOLE_API_URL = f"{GUAC_FULL_URL}/api"
    GUACAMOLE_ADMIN_UNAME = config['connections']['Local']['Guacamole']['AdminUsername']
    GUACAMOLE_ADMIN_PASS = config['connections']['Local']['Guacamole']['AdminPassword']
    LIBVIRT_SECURITY = config['connections']['Local']['Libvirt']['Security']
    LIBVIRT_URL = config['connections']['Local']['Libvirt']['URL']
    file.close()

    return GUAC_SECURITY, GUACAMOLE_URL, GUAC_FULL_URL, GUACAMOLE_API_URL, GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, LIBVIRT_SECURITY, LIBVIRT_URL

def getdaemonvars():
    with open('config.json', 'r') as file:
        config = json.load(file)

    CONNECTION_KEY = config['daemon']['connecton_key']
    LISTENIP = config['daemon']['listenip']
    LISTENPORT = config['daemon']['listenport']
    file.close

    return CONNECTION_KEY, LISTENIP, LISTENPORT

def CreateSession(course, lab):
    GUAC_SECURITY, GUACAMOLE_URL, GUAC_FULL_URL, GUACAMOLE_API_URL, GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, LIBVIRT_SECURITY, LIBVIRT_URL = getvars()
    current_datetime = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    string_length = 10
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=string_length))

    subdirectory_path = os.path.join("sessions", f"{session_id}")
    disks_path = os.path.join(subdirectory_path, "disks")
    os.makedirs(subdirectory_path)
    os.makedirs(disks_path)

    file_path = os.path.join(f"sessions/{session_id}", "session.json")
    session_data = {
        session_id: {
            "Metadata": {
                 "User": "Unused",
                 "Ready": "False",
                 "DateTimeCreated": current_datetime,
                 "CourseLab": f"{course}/{lab}",
                 "isSuspended": False
                },
            "VMinfo":{
                },
            "Networkinfo":{
                },
            "Guacamole":{
                },
            "Questions":{
                },
            "Checkers":{
                },
            "Graders":{
                }
            }
        }

    with open(file_path, 'w') as json_file:
        json.dump(session_data, json_file, indent=4)
        json_file.close()

    return session_id


def generate_vnc_ports(machines):
    vm_vnc_ports = []
    for machine_name, details in machines.items():
        vnc_port = random.randint(49155, 65510)
        vm_vnc_ports.append({f"{machine_name}": vnc_port})

    return vm_vnc_ports

def writecheckers(session_id):

    session_dir = os.path.join(f"sessions", f"{session_id}")
    session_file = os.path.join(f"sessions/{session_id}", "session.json")

    try:
        with open(session_file, 'r') as file:
            session = json.load(file)
    except FileNotFoundError:
        print(f"Session {session_id} not found. Are you sure that is correct?")
        return None

    culab = session[session_id]["Metadata"]["CourseLab"].split('/')
    coursename = culab[0]
    labname = culab[1]
    course_dir = f"courses/{coursename}"
    lab_to_run = f"{course_dir}/labs/{labname}.json"

    file.close()

    with open(lab_to_run, 'r') as file:
        lab = json.load(file)

    checkers = lab[labname]["Checkers"]
    graders = lab[labname]["Graders"]

    for checker_name, checker_info in checkers.items():
        checker_data = {
        "Checker_id" : checker_name,
        "Checker_Type" : checker_info['Checker_Type'],
        "Checker_Task" : checker_info['Checker_Task'],
        "Options" : checker_info['Options'],
        "Machine" : checker_info['Machine'],
        "Checker_Condition" : checker_info['Checker_Condition']
        }

        WriteSessionData("checker", checker_data, session_id)

    for grader_name, grader_info in graders.items():
        graders_data = {
        "Grader_id" : grader_name,
        "Checker_id" : grader_info['Checker_id'],
        "Point_value" : grader_info['Point_value']
        }
        WriteSessionData("grader", graders_data, session_id)
    file.close()

# This Function creates tcomponethe VM envirtonment for the lab.
def CreateVM(machines, networks, vm_vnc_ports, session_id, course_dir):
    GUAC_SECURITY, GUACAMOLE_URL, GUAC_FULL_URL, GUACAMOLE_API_URL, GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, LIBVIRT_SECURITY, LIBVIRT_URL = getvars()
    machineips = []
    machinemacs = []
    for network_name, network_info in networks.items():
        dhcp_leases = ""
        random_number = random.randint(1000, 9999)
        br_name = f"virbr{random_number}"
        mac_addr = generate_random_mac()
        base_ip = generate_random_ip()

        for assignment in network_info.get("ipassignments", []):
            net_machine_name = assignment[0]
            net_ip_address = assignment[1]

            full_ip = replace_ip_pattern(base_ip, net_ip_address)

            for machine_name, details in machines.items():
                for network in details.get("Network", []):
                    vm_mac = generate_random_mac()
                    nic_model = network[0]
                    vm_network_name = network[1]
                    if net_machine_name == machine_name and network_name == vm_network_name:
                        machinemac = {machine_name: vm_mac}
                        machinemacs.append(machinemac)
                    if net_machine_name == machine_name and network_name == vm_network_name:
                        dhcp_lease_string = f"""
                        <host mac='{ vm_mac }' name='{ f"{vm_network_name}_{session_id}" }' ip='{ full_ip }'/>"""
                        dhcp_leases = dhcp_leases + dhcp_lease_string
                        machineip = {machine_name: full_ip}
                        machineips.append(machineip)
                else:
                    pass


        ip_addr = replace_ip_pattern(base_ip, network_info.get("HostAddr"))
        sub_mask = network_info.get("Subnet")

        if network_info.get("Type") == "private":
            bridge_conf = f"""
            <bridge name='{br_name}' stp='on' delay='0'/>
            <mac address='{mac_addr}'/>
            <ip address='{ip_addr}' netmask='{sub_mask}'>
            """
        elif network_info.get("Type") == "internet":
            bridge_conf = f"""
            <forward mode="nat"/>
            <bridge name='{br_name}' stp='on' delay='0'/>
            <mac address='{mac_addr}'/>
            <ip address='{ip_addr}' netmask='{sub_mask}'>
            """
        else:
            print("WARNING: Network not specified, Please check lab config. Destorying session")
            DestorySession(session_id)
            return None



        network_name = f"{network_name}_{session_id}"
        dhcp_start = replace_ip_pattern(base_ip, network_info.get("DHCPv4StartRange"))
        dhcp_end = replace_ip_pattern(base_ip, network_info.get("DHCPv4EndRange"))

        net_xml = generate_net_config(network_name, dhcp_start, dhcp_end, dhcp_leases, bridge_conf)
        create_internal_network(net_xml)

        network_data = {
            "Network_Name": network_name,
            "Type": network_info.get("Type"),
            "HostAddr": ip_addr,
            "Subnet": network_info.get("Subnet"),
            "DHCPv4StartRange": dhcp_start,
            "DHCPv4EndRange": dhcp_end,
            "DHCPleases" : dhcp_leases.replace('\n', ',').replace(' ' * 24, ' ')
            }

        WriteSessionData("network", network_data, session_id)

    for machine_name, details in machines.items():

        for machine_dict in vm_vnc_ports:
            if machine_name in machine_dict:
                vnc_port = machine_dict[machine_name]
            else:
                pass

        disk_conf = ""
        VM_Disks = []
        diski = 0
        driveletter = 'a'
        for disk in details.get("Disks", []):
            for disk_type, path in disk.items():
                if disk_type == "cdrom":
                    source_file_path = f"{course_dir}/vm_images/{path}"
                    destination_file_path = f"sessions/{session_id}/disks/{session_id}_{path}"
                    try:
                        with open(source_file_path, 'rb') as source_file:
                            file_content = source_file.read()

                        with open(destination_file_path, 'wb') as destination_file:
                            destination_file.write(file_content)
                    except Exception as e:
                        print(f'An error occurred: {e}')
                    abspath = os.path.abspath(destination_file_path)

                    disk_string = f""" <disk type="file" device="cdrom">
                    <driver name="qemu" type="raw"/>
                    <source file="{abspath}"/>
                    <target dev="sd{driveletter}" bus="sata"/>
                    <readonly/>
                    <address type="drive" controller="0" bus="0" target="0" unit="{diski}"/>
                 </disk>
                """
                    diski = diski + 1
                    driveletter = chr(ord(driveletter) + 1)

                elif disk_type == "lindisk":
                    source_file_path = f"{course_dir}/vm_images/{path}"
                    destination_file_path = f"sessions/{session_id}/disks/{session_id}_{machine_name}_{path}"
                    try:
                        shutil.copy2(source_file_path, destination_file_path)
                    except Exception as e:
                        print(f"Error: {e}. Option 2 Failed the Lab will not work")

                    abspath = os.path.abspath(destination_file_path)

                    disk_string = f""" <disk type='file' device='disk'>
                    <driver name='qemu' type='qcow2'/>
                    <source file='{abspath}'/>
                    <target dev='vda' bus='virtio'/>
                    <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
                 </disk>
                """
                elif disk_type == "windisk":
                    source_file_path = f"{course_dir}/vm_images/{path}"
                    destination_file_path = f"sessions/{session_id}/disks/{session_id}_{machine_name}_{path}"
                    try:
                        shutil.copy2(source_file_path, destination_file_path)
                    except Exception as e:
                        print(f"Error: {e}. Option 2 Failed the Lab will not work")

                    abspath = os.path.abspath(destination_file_path)

                    disk_string = f""" <disk type='file' device='disk'>
                    <driver name='qemu' type='qcow2'/>
                    <source file='{abspath}'/>
                    <target dev="sd{driveletter}" bus="sata"/>
                    <address type="drive" controller="0" bus="0" target="0" unit="{diski}"/>
                </disk>
                """
                    diski = diski + 1
                    driveletter = chr(ord(driveletter) + 1)

                disk_conf = disk_conf + disk_string
                disk_dict = {disk_type:abspath}
                VM_Disks.append(disk_dict)

        network_conf = ""
        i = 3
        netcount = 0

        machine_data_macs = []
        for machinemac in machinemacs:
            for name, mac in machinemac.items():
                if name == machine_name:
                    machine_data_macs.append(mac)


        for network in details.get("Network", []):
            vm_mac = machine_data_macs[netcount]
            nic_model = network[0]
            network_name = network[1]
            network_string = f"""<interface type='network'>
                    <mac address='{vm_mac}'/>
                    <source network='{network_name}_{session_id}'/>
                    <model type='{nic_model}'/>
                    <address type='pci' domain='0x0000' bus='0x00' slot='0x0{i}' function='0x0'/>
                </interface>
                """
            network_conf = network_conf + network_string
            i = i+2
            netcount = netcount + 1

        machine_data_ips = []
        for machineip in machineips:
            for name, ip in machineip.items():
                if name == machine_name:
                    machine_data_ips.append(ip)

        machine_name = f"{machine_name}_{session_id}"
        vm_xml = generate_vm_config(machine_name, details.get("Memory"), details.get("CPUCores"), vnc_port, network_conf, disk_conf)
        #print(vm_xml)
        create_persistent_virtual_machine(machine_name, vm_xml)

        machine_data = {
            "Machine_Name": machine_name,
            "CPUCores": details.get("CPUCores"),
            "Memory": details.get("Memory"),
            "Networks": details.get("Network", []),
            "Disks": VM_Disks,
            "VNC_Port": vnc_port,
            "machine_data_ips": machine_data_ips,
            "machine_data_macs": machine_data_macs
            }

        WriteSessionData("machine", machine_data, session_id)

    return vm_vnc_ports

def ConfigureGuac(vm_vnc_ports, session_id):
    GUAC_SECURITY, GUACAMOLE_URL, GUAC_FULL_URL, GUACAMOLE_API_URL, GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, LIBVIRT_SECURITY, LIBVIRT_URL = getvars()
    guac_admin_auth_token = generate_authToken(GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, GUACAMOLE_API_URL)
    session_user_credentials = create_guacamole_user(guac_admin_auth_token, GUACAMOLE_API_URL)
    sftp = "false"

    guac_connection_names = []
    for vnc_port in vm_vnc_ports:
        for machine, port in vnc_port.items():
            machine_name = machine
            machine_port = port

        conn_name = f"{machine_name}_{session_id}"
        connection_id = create_guacamole_connections(guac_admin_auth_token, conn_name, machine_port, sftp, GUACAMOLE_API_URL)
        session_username = session_user_credentials["username"]
        set_user_permissions(session_username, connection_id, guac_admin_auth_token, GUACAMOLE_API_URL)
        guac_connection_names.append({f"{conn_name}": f"{connection_id}"})

    session_user_auth_token = generate_authToken(session_user_credentials["username"], session_user_credentials["password"], GUACAMOLE_API_URL)
    session_client_urls = get_client_url(session_user_auth_token, f"{GUAC_SECURITY}://{GUACAMOLE_URL}")

    guac_data = {
        "Connection_Name": conn_name,
        "Session_User": session_user_credentials["username"],
        "Session_Password": session_user_credentials["password"],
        "Session_Auth_Token": session_user_auth_token,
        "Session_Connection_Names": guac_connection_names,
        "Session_Client_URLs": session_client_urls
        }

    WriteSessionData("guacamole", guac_data, session_id)

    return guac_data

def PauseSession(session_id):
    GUAC_SECURITY, GUACAMOLE_URL, GUAC_FULL_URL, GUACAMOLE_API_URL, GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, LIBVIRT_SECURITY, LIBVIRT_URL = getvars()
    guac_admin_auth_token = generate_authToken(GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, GUACAMOLE_API_URL)
    session_dir = os.path.join(f"sessions", f"{session_id}")
    session_file = os.path.join(f"sessions/{session_id}", "session.json")
    try:
        with open(session_file, 'r') as file:
            session = json.load(file)
    except FileNotFoundError:
        print(f"Session {session_id} not found. Are you sure that is correct?")
        return None

    machines = session[session_id]["VMinfo"]
    machine_names = list(machines.keys())
    for machine_name in machine_names:
        power_off_vm(machine_name)

    networks = session[session_id]["Networkinfo"]
    network_names = list(networks.keys())
    for network_name in network_names:
        pause_internal_network(network_name)

    guac_connections = session[session_id]["Guacamole"]["Session_Connection_Names"]
    session_user = session[session_id]["Guacamole"]["Session_User"]
    for guac_connection in guac_connections:
        for connection_name, connection_id in guac_connection.items():
            revoke_user_permissions(session_user, connection_id, guac_admin_auth_token, GUACAMOLE_API_URL)

    print(f"Session {session_id} has been paused sucessfully!")

    return None

def ResumeSession(session_id):
    GUAC_SECURITY, GUACAMOLE_URL, GUAC_FULL_URL, GUACAMOLE_API_URL, GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, LIBVIRT_SECURITY, LIBVIRT_URL = getvars()
    guac_admin_auth_token = generate_authToken(GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, GUACAMOLE_API_URL)
    session_dir = os.path.join(f"sessions", f"{session_id}")
    session_file = os.path.join(f"sessions/{session_id}", "session.json")

    try:
        with open(session_file, 'r') as file:
            session = json.load(file)
    except FileNotFoundError:
        print(f"Session {session_id} not found. Are you sure that is correct?")
        return None

    culab = session[session_id]["Metadata"]["CourseLab"].split('/')
    coursename = culab[0]
    labname = culab[1]
    course_dir = f"courses/{coursename}"
    lab_to_run = f"{course_dir}/labs/{labname}.json"

    with open(lab_to_run, 'r') as file:
        lab = json.load(file)

    instructions = lab[labname]["Instructions"]
    file.close()

    networks = session[session_id]["Networkinfo"]
    network_names = list(networks.keys())
    for network_name in network_names:
        resume_internal_network(network_name)

    machines = session[session_id]["VMinfo"]
    machine_names = list(machines.keys())
    for machine_name in machine_names:
        power_on_vm(machine_name)

    guac_connections = session[session_id]["Guacamole"]["Session_Connection_Names"]
    session_user = session[session_id]["Guacamole"]["Session_User"]
    for guac_connection in guac_connections:
        for connection_name, connection_id in guac_connection.items():
            set_user_permissions(session_user, connection_id, guac_admin_auth_token, GUACAMOLE_API_URL)

    session_user_auth_token = generate_authToken(session[session_id]["Guacamole"]["Session_User"], session[session_id]["Guacamole"]["Session_Password"], GUACAMOLE_API_URL)
    Session_Client_URLs = session[session_id]["Guacamole"]["Session_Client_URLs"]
    guac_data = {
        "Session_Auth_Token": session_user_auth_token,
        "Session_Client_URLs": Session_Client_URLs
    }

    renderedlab = GenerateLab(GUAC_FULL_URL, guac_data, session_id, instructions, 1)

    print(f"Session {session_id} has been resumed sucessfully!")

    return renderedlab

def DestorySession(session_id):
    GUAC_SECURITY, GUACAMOLE_URL, GUAC_FULL_URL, GUACAMOLE_API_URL, GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, LIBVIRT_SECURITY, LIBVIRT_URL = getvars()

    guac_admin_auth_token = generate_authToken(GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, GUACAMOLE_API_URL)
    session_dir = os.path.join(f"sessions", f"{session_id}")
    session_file = os.path.join(f"sessions/{session_id}", "session.json")
    try:
        with open(session_file, 'r') as file:
            session = json.load(file)
    except FileNotFoundError:
        print(f"Session {session_id} not found. Are you sure that is correct?")
        return None

    machines = session[session_id]["VMinfo"]
    machine_names = list(machines.keys())
    for machine_name in machine_names:
        force_off_vm(machine_name)
        delete_virtual_machine(machine_name)


    networks = session[session_id]["Networkinfo"]
    network_names = list(networks.keys())
    for network_name in network_names:
        delete_internal_network(network_name)

    guac_connections = session[session_id]["Guacamole"]["Session_Connection_Names"]
    guac_user = session[session_id]["Guacamole"]["Session_User"]
    for guac_connection in guac_connections:
        for connection_name, connection_id in guac_connection.items():
            delete_guacamole_connections(guac_admin_auth_token, connection_id, GUACAMOLE_API_URL)
    delete_guacamole_user(guac_admin_auth_token, guac_user, GUACAMOLE_API_URL)

    shutil.rmtree(session_dir)

    print(f"Session {session_id} has been destroyed sucessfully!")

    return None

def startLab(session_id):
    GUAC_SECURITY, GUACAMOLE_URL, GUAC_FULL_URL, GUACAMOLE_API_URL, GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, LIBVIRT_SECURITY, LIBVIRT_URL = getvars()
    session_file = os.path.join(f"sessions/{session_id}", "session.json")
    try:
        with open(session_file, 'r') as file:
            session = json.load(file)
    except FileNotFoundError:
        print(f"Session {session_id} not found. Are you sure that is correct?")
        return None
    culab = session[session_id]["Metadata"]["CourseLab"].split('/')

    course = culab[0]
    labname = culab[1]
    course_dir = f"courses/{course}"
    lab_to_run = f"{course_dir}/labs/{labname}.json"
    file.close()

    with open(lab_to_run, 'r') as file:
        lab = json.load(file)

    machines = lab[labname]["Machines"]
    networks = lab[labname]["Networks"]
    instructions = lab[labname]["Instructions"]

    writecheckers(session_id)
    vm_vnc_ports = generate_vnc_ports(machines)
    guac_data = ConfigureGuac(vm_vnc_ports, session_id)
    CreateVM(machines, networks, vm_vnc_ports, session_id, course_dir)
    writecheckers(session_id)
    WriteSessionData("metadata", {"Ready":"True"}, session_id)
    file.close()

    return session_id

def RenderLabPage(session_id):
    GUAC_SECURITY, GUACAMOLE_URL, GUAC_FULL_URL, GUACAMOLE_API_URL, GUACAMOLE_ADMIN_UNAME, GUACAMOLE_ADMIN_PASS, LIBVIRT_SECURITY, LIBVIRT_URL = getvars()
    session_file = os.path.join(f"sessions/{session_id}", "session.json")
    try:
        with open(session_file, 'r') as file:
            session = json.load(file)
    except FileNotFoundError:
        print(f"Session {session_id} not found. Are you sure that is correct?")
        return None

    Session_Client_URLs = session[session_id]["Guacamole"]["Session_Client_URLs"]
    session_user_auth_token = session[session_id]["Guacamole"]["Session_Auth_Token"]
    guac_data = {
        "Session_Auth_Token": session_user_auth_token,
        "Session_Client_URLs": Session_Client_URLs
    }
    culab = session[session_id]["Metadata"]["CourseLab"].split('/')
    file.close()

    coursename = culab[0]
    labname = culab[1]
    course_dir = f"courses/{coursename}"
    lab_to_run = f"{course_dir}/labs/{labname}.json"

    with open(lab_to_run, 'r') as file:
        lab = json.load(file)

    instructions = lab[labname]["Instructions"]
    file.close()

    renderedlab = GenerateLab(GUAC_FULL_URL, guac_data, session_id, instructions, 0)
    return renderedlab

@app.route('/newsession', methods=['POST'])
def cnewsession():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    labtorun = inputdata.get('labtorun', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    culab = labtorun.split('/')
    coursename = culab[0]
    labname = culab[1]
    if CONNECTION_KEY == input_connecton_key:
        session_id = CreateSession(coursename, labname)
        data = {
            'session_id' : session_id,
            'action_id' : 0
            }
        return jsonify(data)
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401

@app.route('/buildsession', methods=['POST'])
def busession():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    session_id = inputdata.get('session_id', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    if CONNECTION_KEY == input_connecton_key:
        session_id = startLab(session_id)
        data = {
            'session_id' : session_id,
            'action_id' : 1
            }
        return jsonify(data)
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401

@app.route('/renderlab', methods=['POST'])
def renderLab():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    session_id = inputdata.get('session_id', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    if CONNECTION_KEY == input_connecton_key:
        renderedlab =  RenderLabPage(session_id)
        data = {
            'session_id' : session_id,
            'message' : f"Lab has been rendered",
            'renderedlab' : renderedlab,
            'action_id' : 2
            }
        return jsonify(data)
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401
@app.route('/destorysession', methods=['POST'])
def dsession():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    session_id = inputdata.get('session_id', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    if CONNECTION_KEY == input_connecton_key:
        DestorySession(session_id)
        data = {
            'session_id' : session_id,
            'message' : f"session has been destoryed",
            'action_id' : 3
            }
        return jsonify(data)
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401

@app.route('/pausesession', methods=['POST'])
def psession():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    session_id = inputdata.get('session_id', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    if CONNECTION_KEY == input_connecton_key:
        PauseSession(session_id)
        data = {
            'session_id' : session_id,
            'message' : f"session has been paused",
            'action_id' : 4
            }
        return jsonify(data)
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401

@app.route('/resumesession', methods=['POST'])
def rsession():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    session_id = inputdata.get('session_id', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    if CONNECTION_KEY == input_connecton_key:
        renderedlab = ResumeSession(session_id)
        data = {
            'session_id' : session_id,
            'message' : f"session has been resumed",
            'renderedlab' : renderedlab,
            'action_id' : 5
            }
        return jsonify(data)
    else:
        return jsonify({"Error" : "Backend Key Incorrect"})

@app.route('/probesession', methods=['POST'])
def prsession():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    session_id = inputdata.get('session_id', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    if CONNECTION_KEY == input_connecton_key:
        try:
            session_file = os.path.join(f"sessions/{session_id}", "session.json")
            with open(session_file, 'r') as file:
                session = json.load(file)

            status = session[session_id]["Metadata"]["Ready"]
        except:
            status = 'false'
        data = {
            'session_id' : session_id,
            'message' : f"session has been probed",
            'status' : status,
            'action_id' : 9
            }
        file.close()
        return jsonify(data)
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401

@app.route('/installedlabs', methods=['POST'])
def installedlabs():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    if CONNECTION_KEY == input_connecton_key:
        try:
            courses_file = os.path.join(f"courses", "courses.json")
            with open(courses_file, 'r') as file:
                data = json.load(file)

            available_labs = []
            available_disks = []
            for course_name, course_details in data["Courses"].items():
                cname = f"{course_name}"
                cdisc = f"{course_details['Description']}"

                for image_number, image_info in course_details["DiskImages"].items():
                    diskdata = [image_number, image_info[0], image_info[1]]
                    available_disks.append(diskdata)

                for lab_number, lab_info in course_details["Labs"].items():
                    labformat = f"{course_name.lower()}/{lab_info[0].lower()}"
                    lab = [lab_number, lab_info[0], lab_info[1], labformat]
                    available_labs.append(lab)

            resdata = {
                'CourseDesription': cdisc,
                'available_disks': available_disks,
                'available_labs': available_labs
                }

        except:
            resdata = {
                'Error': 'Courses File does not exist! Check this node'
                }
        file.close()
        return jsonify({cname : resdata})
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401

@app.route('/serverstats', methods=['POST'])
def serverstats():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()

    if CONNECTION_KEY == input_connecton_key:
        directory_path = "sessions"
        entries = os.listdir(directory_path)
        session_count = sum(os.path.isdir(os.path.join(directory_path, entry)) for entry in entries) - 1

        ram = psutil.virtual_memory()
        cpu = psutil.cpu_percent(percpu=True)
        data = {
        'cpupercent' : f"{round(sum(cpu) / len(cpu), 2)}",
        'cpucorespercent' : f"{cpu}",
        'totalram' : f"{ram.total / (1024 ** 3):.2f}",
        'availram' : f"{ram.available / (1024 ** 3):.2f}",
        'useram' : f"{ram.used / (1024 ** 3):.2f}",
        'rampercent' : f"{ram.percent:.2f}",
        'session_count': session_count
        }
        return jsonify(data)
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401

@app.route('/runchecker', methods=['POST'])
def runcheckerfunction():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    session_id = inputdata.get('session_id', 'NOTPROVIDED')
    checker_id = inputdata.get('checker_id', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    if CONNECTION_KEY == input_connecton_key:
        try:
            session_file = os.path.join(f"sessions/{session_id}", "session.json")
            with open(session_file, 'r') as file:
                session = json.load(file)

            if checker_id == 'NOTPROVIDED':
                checkers_list = []
                print("Checker ID Not provided. Running through all lab checkers")

                for chkname in session[session_id]["Checkers"]:
                    checkers_list.append(chkname)
            else:
                checkers_list = [checker_id]

            answers = {}
            for checker in checkers_list:
                checkertype = session[session_id]["Checkers"][checker]["Checker_Type"]
                checkertask = session[session_id]["Checkers"][checker]["Checker_Task"]
                checkercondition = session[session_id]["Checkers"][checker]["Checker_Condition"]
                submited = session[session_id]["Checkers"][checker]["Submitted"]
                machine = session[session_id]["Checkers"][checker]["Machine"]
                options = session[session_id]["Checkers"][checker]["Options"]


                if checkertype == "question":
                    correct = session[session_id]["Questions"][f'{session_id}_{checkertask}']["Answer"]
                    submited = session[session_id]["Questions"][f'{session_id}_{checkertask}']["Submitted"]

                    if correct == submited:
                        answer = True
                        answered = True
                    elif submited == "null":
                        answer = False
                        answered = False
                    else:
                        answer = False
                        answered = True

                    checker_update_data= {
                        "Checker_id": checker,
                        "Correct": answer,
                        "Submitted": answered
                    }
                    WriteSessionData("checkerupdate", checker_update_data, session_id)
                else:
                    machines = session[session_id]["VMinfo"]
                    machine_names = list(machines.keys())
                    for machine_name in machine_names:
                        if machine_name == f"{machine}_{session_id}":
                            machineip = session[session_id]["VMinfo"][f"{machine}_{session_id}"]["machine_data_ips"][0]
                            answer = runchecker(checkertype, checkertask, checkercondition, machineip, options)
                            checker_update_data= {
                                "Checker_id": checker,
                                "Correct": answer,
                                "Submitted": True
                            }
                            WriteSessionData("checkerupdate", checker_update_data, session_id)
                        else:
                            pass
        except Exception as e:
            print({e})
            return jsonify({"Error" : f"An Error has Occured {e}"}), 401

        data = {
            'session_id' : session_id,
            'message' : f"Checkers have been run. Please check the session file",
            'action_id' : 11
            }

        file.close()
        return jsonify(data)
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401


@app.route('/rungrader', methods=['POST'])
def rungradersfunction():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    session_id = inputdata.get('session_id', 'NOTPROVIDED')
    grader_id = inputdata.get('grader_id', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    if CONNECTION_KEY == input_connecton_key:
        try:
            session_file = os.path.join(f"sessions/{session_id}", "session.json")
            with open(session_file, 'r') as file:
                session = json.load(file)

            if grader_id == 'NOTPROVIDED':
                graders_list = []
                print("Grader ID Not provided. Running through all lab graders")

                for grname in session[session_id]["Graders"]:
                    graders_list.append(grname)
            else:
                graders_list = [grader_id]

            points = 0
            correct = 0
            incorrect = 0
            unanswered = 0
            totalpoints = 0

            for grader in graders_list:
                checker = session[session_id]["Graders"][grader]["Checker_id"]
                iscorrect = session[session_id]["Checkers"][f"{checker}_{session_id}"]["Correct"]
                issubmited = session[session_id]["Checkers"][f"{checker}_{session_id}"]["Submitted"]
                pointval = int(session[session_id]["Graders"][grader]["Point_value"])

                if issubmited == True and iscorrect == True:
                    points = points + pointval
                    correct = correct + 1
                    totalpoints = totalpoints + pointval
                elif issubmited == True and iscorrect == False:
                    points = points
                    incorrect = incorrect + 1
                    totalpoints = totalpoints + pointval
                elif issubmited == False:
                    points = points
                    unanswered = unanswered + 1
                    totalpoints = totalpoints + pointval
        except Exception as e:
            print({e})
            return jsonify({"Error" : f"An Error has Occured {e}"}), 401
        data = {
            'session_id' : session_id,
            'message' : f"Graders have been run. Here are the results",
            'points_awarded': points,
            'total_points': totalpoints,
            'correct': correct,
            'incorrect': incorrect,
            'unanswered': unanswered,
            'action_id' : 12
        }

        file.close()
        return jsonify(data)
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401

@app.route('/answerquestion', methods=['POST'])
def answerquestionfunction():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    session_id = inputdata.get('session_id', 'NOTPROVIDED')
    question_number = inputdata.get('question_number', 'NOTPROVIDED')
    answer = inputdata.get('answer', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    if CONNECTION_KEY == input_connecton_key:
        question_data = {
            "question_number": question_number,
            "answer": answer
        }
        WriteSessionData("questionupdate", question_data, session_id)
        return jsonify({"Notice" : "Question has been answered"}), 200
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401

@app.route('/machinecontrol', methods=['POST'])
def machinecontrolfunction():
    inputdata = request.get_json()
    input_connecton_key = inputdata.get('connecton_key', 'NOTPROVIDED')
    session_id = inputdata.get('session_id', 'NOTPROVIDED')
    action = inputdata.get('action', 'NOTPROVIDED')
    machine = inputdata.get('machine', 'NOTPROVIDED')
    CONNECTION_KEY, LISTENIP, LISTENPORT = getdaemonvars()
    if CONNECTION_KEY == input_connecton_key:
        machine_name = f"{machine}_{session_id}"
        if action == "shutdown":
            power_off_vm(machine_name)
        elif action == "poweron":
            power_on_vm(machine_name)
        elif action == "forceoff":
            force_off_vm(machine_name)
        else:
            return jsonify({"Error" : f"Action {action} not supported"}), 200
        return jsonify({"Notice" : f"Action {action} on {machine} has been complete"}), 200
    else:
        return jsonify({"Error" : "Backend Key Incorrect"}), 401

if __name__ == '__main__':
    print("Please use the gunicorn python script to launch the program.")
    #app.run(debug=False, host=LISTENIP, port=LISTENPORT)
