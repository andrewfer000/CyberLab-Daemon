import subprocess, signal, os, sys
import json

def getdaemonvars():
    with open('config.json', 'r') as file:
        config = json.load(file)

    LISTENIP = config['daemon']['listenip']
    LISTENPORT = config['daemon']['listenport']
    file.close

    return LISTENIP, LISTENPORT

def run_gunicorn(LISTENIP, LISTENPORT):
    command = [
        "gunicorn",
        "-w", "8",
        "-b", f"{LISTENIP}:{LISTENPORT}",
        "-t", "240",
        "app:app",
    ]
    process = subprocess.Popen(command)

    # Set up a signal handler to capture SIGINT (Ctrl+C) and SIGTERM signals
    def handle_signals(signum, frame):
        print("Terminating Gunicorn process...")
        process.terminate()
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, handle_signals)
    signal.signal(signal.SIGTERM, handle_signals)

    # Wait for the subprocess to complete
    process.communicate()

if __name__ == "__main__":
    LISTENIP, LISTENPORT = getdaemonvars()
    run_gunicorn(LISTENIP, LISTENPORT)
