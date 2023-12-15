import requests, argparse, json, os

def recordsession(daemonname, sessionid):
    file_path = os.path.join(f"daemontracker.json")

    with open(file_path, 'r') as file:
        data = json.load(file)
    file.close()

    data[sessionid] = daemonname

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
    file.close()

def getdaemonname(session_id):
    file_path = os.path.join(f"daemontracker.json")
    with open(file_path, 'r') as file:
        data = json.load(file)

    daemonname = ""
    for key, value in data.items():
        if key == session_id:
            daemonname = value
        else:
            pass
    file.close()
    return daemonname

def selectdaemontest(labtorun):
    with open('daemon.json', 'r') as file:
        daemonsfile = json.load(file)

    daemons = daemonsfile['daemons']
    daemonlist = []
    for daemonname, daemon in daemons.items():
        api_url = daemon['api_url']
        connecton_key = daemon['connecton_key']

        labavailable = False
        cutilization = -1
        mutilization = -1

        base_url = f"{api_url}/installedlabs"
        data = {
            'connecton_key': connecton_key
        }
        try:
            response = requests.post(base_url, json=data)
            if response.status_code == 200:
                data = response.json()

                lablist = []
                for coursename in data:
                    for item in data[coursename]["available_labs"]:
                        lablist.append(item[3])
            else:
                print(f'Request failed with status code: {response.status_code}')

        except requests.RequestException as e:
            print(f'Request encountered an error: {e}')

        if labtorun in lablist:
            labavailable = True
        else:
            pass

        if labavailable == True:
            base_url = f"{api_url}/serverstats"
            data = {
                'connecton_key': connecton_key
            }
            try:
                response = requests.post(base_url, json=data)
                if response.status_code == 200:
                    data = response.json()
                    mutilization = data['rampercent']
                    cutilization = data['cpupercent']
                    sessioncount = data['session_count']

                    daemoninfo = [daemonname, mutilization, cutilization, sessioncount]
                    daemonlist.append(daemoninfo)

                else:
                    print(f'Request failed with status code: {response.status_code}')

            except requests.RequestException as e:
                print(f'Request encountered an error: {e}')
        else:
            pass

    print(f"Daemons with '{labtorun}' installed: {daemonlist}")
    if len(daemonlist) > 1:
        print("daemon list larger than 1. Selecting Server with lowest load")
        # Logic to select lowest load server goes here
    else:
       print(f"The daemon you should use is: {daemonlist[0][0]}")
       return daemonlist[0][0]

def getdaemonvars(daemonname="Default"):
    with open('daemon.json', 'r') as file:
        daemon = json.load(file)

    try:
        API_URL = daemon['daemons'][daemonname]['api_url']
        CONNECTON_KEY = daemon['daemons'][daemonname]['connecton_key']
    except:
        print("ERROR: Daemon not found: Please ensure the daemon you selected is configured!")
        API_URL = "NOTPROVIDED"
        CONNECTON_KEY = "NOTPROVIDED"
    file.close

    return API_URL, CONNECTON_KEY

def newsessiontest(labtorun, daemontouse):

    if daemontouse == "auto":
        daemonname = selectdaemontest(labtorun)
    else:
        daemonname = daemontouse

    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/newsession"
    timeout = 300

    data = {
        'labtorun': labtorun,
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data, timeout=timeout)
        if response.status_code == 200:
            api_data = response.json()
            text_value = api_data.get('session_id', {})
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')
        text_value = ""

    recordsession(daemonname, text_value)
    return text_value, daemonname

def buildsessiontest(session_id):
    daemonname = getdaemonname(session_id)
    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/buildsession"
    data = {
        'session_id': session_id,
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            print(response.json())  # For JSON response
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def pausesessiontest(session_id, daemonname="Default"):
    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/pausesession"
    data = {
        'session_id': session_id,
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            print(response.json())  # For JSON response
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def destorysessiontest(session_id):
    daemonname = getdaemonname(session_id)
    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/destorysession"

    data = {
        'session_id': session_id,
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            print(response.json())  # For JSON response
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def resumesessiontest(session_id):
    daemonname = getdaemonname(session_id)
    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/resumesession"

    data = {
        'session_id': session_id,
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            api_data = response.json()
            text_value = api_data.get('renderedlab', {})
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

    with open(f'{session_id}_labpage.html', 'w') as outfile:
        outfile.write(text_value)

def renderlabtest(session_id):
    daemonname = getdaemonname(session_id)
    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/renderlab"

    data = {
        'session_id': session_id,
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            api_data = response.json()
            text_value = api_data.get('renderedlab', {})
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

    with open(f'{session_id}_labpage.html', 'w') as outfile:
        outfile.write(text_value)


def probesessiontest(session_id):
    daemonname = getdaemonname(session_id)
    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/probesession"

    data = {
        'session_id': session_id,
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            print(response.json())  # For JSON response
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def installedlabtests(daemonname):
    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/installedlabs"
    data = {
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            data = response.json()  # For JSON response
            print(json.dumps(data, indent=4, sort_keys=False))

            lablist = []
            for coursename in data:
                for item in data[coursename]["available_labs"]:
                    lablist.append(item[3])
            print(f" \nRaw Lab List: {lablist}")
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def daemonchecktest(daemonname):

    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/serverstats"

    data = {
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=4, sort_keys=True))
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def checksessiontest(session_id):
    daemonname = getdaemonname(session_id)
    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/runchecker"
    data = {
        'session_id': session_id,
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            print(response.json())  # For JSON response
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def gradesessiontest(session_id):
    daemonname = getdaemonname(session_id)
    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/rungrader"
    data = {
        'session_id': session_id,
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=4, sort_keys=True))
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def answerquestiontest(session_id, question_number, answer):
    daemonname = getdaemonname(session_id)
    API_URL, CONNECTON_KEY = getdaemonvars(daemonname)
    base_url = f"{API_URL}/answerquestion"
    data = {
        'session_id': session_id,
        'connecton_key': CONNECTON_KEY,
        'question_number': question_number,
        'answer': answer
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            print(response.json())  # For JSON response
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CyberLab Backend API CLI Program")
    parser.add_argument("--demosession", action="store", help="--demosession [course/lab] Selects a daemon, Creates a new session, Builds the session, renders the lab")
    parser.add_argument("--submit", action="store", help="--shutsession [session_id] will check, grade, and destory the session")
    parser.add_argument("--newsession", action="store", help="Selects a daemon and Creates a new session")
    parser.add_argument("--buildsession", action="store", help="--buildsesion [session-id] will build the session for the given session_id")
    parser.add_argument("--destorysession", action="store", help="--destorysession [session-id] will stop and delete the VMs, Guacamole connections/users and files for the session")
    parser.add_argument("--pausesession", action="store", help="--pausesession [session-id] will stop VMs and revoke guacamole permissions until session is resumed")
    parser.add_argument("--resumesession", action="store", help="--resumesession [session-id] will resume VMs and add guacamole permissions to the session user")
    parser.add_argument("--probesession", action="store", help="--probesession [session-id] will check to see if a lab session is ready to go")
    parser.add_argument("--renderlab", action="store", help="--renderlab [session-id] will render the lab page for a given session")
    parser.add_argument("--runchecker", action="store", help="--runchecker [session-id] will run the checkers for a session")
    parser.add_argument("--rungrader", action="store", help="--rungrader [session-id] will run the graders for a session and output the results")
    parser.add_argument("--listlabs", action="store", help="--listlabs [daemon] will return a list of labs you can run on a daemon")
    parser.add_argument("--daemoninfo", action="store", help="--daemoninfo [daemon] will let you know the stats of a daemon")
    parser.add_argument("--selectdaemon", action="store", help="--selectdaemon [course/lab] selects the optimal daemon for a lab session")
    parser.add_argument('--answerquestion', nargs='+', help="--answerquestion [session_id] [question_number] [answer] submits an text-question answer to a lab")
    args = parser.parse_args()

    if args.newsession:
        print("Building your session. Please wait")
        session_id = newsessiontest(args.newsession, "auto")
        print(f"Session ID: {session_id}")
    elif args.buildsession:
        print(f"Building Session For {args.buildsession}")
        buildsessiontest(args.buildsession)
    elif args.renderlab:
        print(f"Rendering Lab For {args.renderlab}")
        renderlabtest(args.renderlab)
    elif args.pausesession:
        print(f"Pausing Session {args.pausesession}")
        pausesessiontest(args.pausesession)
    elif args.resumesession:
        print(f"Resuming Session {args.resumesession}")
        resumesessiontest(args.resumesession)
    elif args.destorysession:
        print(f"Destorying Session {args.destorysession}")
        destorysessiontest(args.destorysession)
    elif args.probesession:
        print(f"Probeing Session {args.probesession}")
        probesessiontest(args.probesession)
    elif args.runchecker:
        print(f"Running Checkers on Session {args.runchecker}")
        checksessiontest(args.runchecker)
    elif args.rungrader:
        print(f"Running Graders on Session {args.rungrader}")
        gradesessiontest(args.rungrader)
    elif args.selectdaemon:
        selectdaemontest(args.selectdaemon)
    elif args.listlabs:
        installedlabtests(args.listlabs)
    elif args.daemoninfo:
        daemonchecktest(args.daemoninfo)
    elif args.answerquestion:
        if len(args.answerquestion) >= 3:
            session_id = args.answerquestion[0]
            question_number = int(args.answerquestion[1])
            answer = args.answerquestion[2]
            answerquestiontest(session_id, question_number, answer)
        else:
            print('Please provide a session_id, question_number, and answer.')
    elif args.demosession:
        print(f"Building Session For {args.demosession}")
        session_id, daemonname = newsessiontest(args.demosession, "auto")
        buildsessiontest(session_id)
        renderlabtest(session_id)
        print(f"SessionID: {session_id} has been built and rendered")
    elif args.submit:
        print(f"Checking, Grading, and Destorying {args.submit}")
        checksessiontest(args.submit)
        gradesessiontest(args.submit)
        print("")
        destorysessiontest(args.submit)
        print(f"SessionID: {args.submit} has been graded and destoryed")
    else:
        print("Invaild Option")
