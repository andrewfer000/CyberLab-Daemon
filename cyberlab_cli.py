import requests, argparse, json

API_URL = 'http://127.0.0.1:5000'

def newsessiontest(labtorun):
    base_url = f"{API_URL}/newsession"
    timeout = 300

    # Define query parameters as a dictionary
    params = {
        'labtorun': labtorun,
    }
    try:
        response = requests.get(base_url, params=params, timeout=timeout)
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
    base_url = f"{API_URL}/buildsession"
    # Define query parameters as a dictionary
    params = {
        'session_id': session_id,
    }
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            print(response.json())  # For JSON response
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def pausesessiontest(session_id):
    base_url = f"{API_URL}/pausesession"
    # Define query parameters as a dictionary
    params = {
        'session_id': session_id,
    }
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            print(response.json())  # For JSON response
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def destorysessiontest(session_id):
    base_url = f"{API_URL}/destorysession"

    # Define query parameters as a dictionary
    params = {
        'session_id': session_id,
    }
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            print(response.json())  # For JSON response
        else:
            print(f'Request failed with status code: {response.status_code}')

    except requests.RequestException as e:
        print(f'Request encountered an error: {e}')

def resumesessiontest(session_id):
    base_url = f"{API_URL}/resumesession"

    # Define query parameters as a dictionary
    params = {
        'session_id': session_id,
    }
    try:
        response = requests.get(base_url, params=params)
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
    base_url = f"{API_URL}/renderlab"

    # Define query parameters as a dictionary
    params = {
        'session_id': session_id,
    }
    try:
        response = requests.get(base_url, params=params)
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
    base_url = f"{API_URL}/probesession"

    # Define query parameters as a dictionary
    params = {
        'session_id': session_id,
    }
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            print(response.json())  # For JSON response
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
    else:
        print("Invaild Option")
