import requests, argparse, json

def getdaemonvars():
    with open('daemon.json', 'r') as file:
        daemon = json.load(file)

    API_URL = daemon['daemon']['api_url']
    CONNECTON_KEY = daemon['daemon']['connecton_key']
    file.close

    return API_URL, CONNECTON_KEY

def newsessiontest(labtorun):
    API_URL, CONNECTON_KEY = getdaemonvars()
    base_url = f"{API_URL}/newsession"
    timeout = 300

    # Define query parameters as a dictionary
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

    return text_value

def buildsessiontest(session_id):
    API_URL, CONNECTON_KEY = getdaemonvars()
    base_url = f"{API_URL}/buildsession"
    # Define query parameters as a dictionary
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

def pausesessiontest(session_id):
    API_URL, CONNECTON_KEY = getdaemonvars()
    base_url = f"{API_URL}/pausesession"
    # Define query parameters as a dictionary
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
    API_URL, CONNECTON_KEY = getdaemonvars()
    base_url = f"{API_URL}/destorysession"

    # Define query parameters as a dictionary
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
    API_URL, CONNECTON_KEY = getdaemonvars()
    base_url = f"{API_URL}/resumesession"

    # Define query parameters as a dictionary
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
    API_URL, CONNECTON_KEY = getdaemonvars()
    base_url = f"{API_URL}/renderlab"

    # Define query parameters as a dictionary
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
    API_URL, CONNECTON_KEY = getdaemonvars()
    base_url = f"{API_URL}/probesession"

    # Define query parameters as a dictionary
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

def installedlabtests():
    API_URL, CONNECTON_KEY = getdaemonvars()
    base_url = f"{API_URL}/installedlabs"
    data = {
        'connecton_key': CONNECTON_KEY
    }
    try:
        response = requests.post(base_url, json=data)
        if response.status_code == 200:
            data = response.json()  # For JSON response
            print(json.dumps(data, indent=4, sort_keys=True))
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def daemonchecktest():
    API_URL, CONNECTON_KEY = getdaemonvars()
    base_url = f"{API_URL}/serverstats"

    # Define query parameters as a dictionary
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CyberLab Backend API CLI Program")
    parser.add_argument("--demosession", action="store", help="Creates a new session, Builds the session, renders the lab")
    parser.add_argument("--newsession", action="store", help="Creates a new session")
    parser.add_argument("--buildsession", action="store", help="--buildsesion [session-id] will build the session for the given session_id")
    parser.add_argument("--destorysession", action="store", help="--destorysession [session-id] will stop and delete the VMs, Guacamole connections/users and files for the session")
    parser.add_argument("--pausesession", action="store", help="--pausesession [session-id] will stop VMs and revoke guacamole permissions until session is resumed")
    parser.add_argument("--resumesession", action="store", help="--resumesession [session-id] will resume VMs and add guacamole permissions to the session user")
    parser.add_argument("--probesession", action="store", help="--probesession [session-id] will check to see if a lab session is ready to go")
    parser.add_argument("--renderlab", action="store", help="--renderlab [session-id] will render the lab page for a given session")
    parser.add_argument("--listlabs", action="store_true", help="--listlabs will return a list of labs you can run")
    parser.add_argument("--daemoninfo", action="store_true", help="--daemoninfo will let you know the stats of a daemon")
    args = parser.parse_args()

    if args.newsession:
        print("Building your session. Please wait")
        session_id = newsessiontest(args.newsession)
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
    elif args.demosession:
        print(f"Building Session For {args.demosession}")
        session_id = newsessiontest(args.demosession)
        print(f"SessionID: {session_id} has been created")
        buildsessiontest(session_id)
        print(f"SessionID: {session_id} has been built")
        renderlabtest(session_id)
    elif args.listlabs:
        installedlabtests()
    elif args.daemoninfo:
        daemonchecktest()
    else:
        print("Invaild Option")
