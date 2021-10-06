import threading
import requests
import traceback
import time
import os
import json
import atexit
import subprocess
import logging
import sys
import configparser
from pathlib import Path


# BEGIN Parsing config
config = configparser.ConfigParser()
config.read("supervisor-config.ini")
default_config = config["DEFAULT"]
SUBMITTED_WORK_FILENAME = default_config["SubmittedWorkFilename"]
WORKER_EXECUTABLE_PATH = default_config["WorkerExecutablePath"]
VALID_NONCES_DIRECTORY = default_config["ValidNoncesDirectory"]
CONTROLLER_URI = default_config["ControllerUri"]
# END

def create_valid_nonces_directory():
    if not os.path.exists(VALID_NONCES_DIRECTORY):
        os.mkdir(VALID_NONCES_DIRECTORY)


def get_or_init_submitted_nonces() -> set[str]:
    fle = Path(SUBMITTED_WORK_FILENAME)
    fle.touch(exist_ok=True)

    with open(SUBMITTED_WORK_FILENAME, 'r') as f:
        return set(map(lambda n: str.lower(str.strip(n)), f.readlines()))


def append_submitted_nonce(nonce):
    with open(SUBMITTED_WORK_FILENAME, 'a+') as f:
        f.write(nonce)
        f.write('\n')


def spawn_worker(sender_bits, last_mined_assets, difficulty_target, nonces_directory):
    if not os.path.exists(WORKER_EXECUTABLE_PATH):
        raise Exception(f"Worker Executable Path '{WORKER_EXECUTABLE_PATH}' not found!")

    # The worker will start at a random nonce between 0 and 2^64
    return subprocess.Popen([
        WORKER_EXECUTABLE_PATH,
        '-a', sender_bits,
        '-l', last_mined_assets,
        '-d', difficulty_target,
        '-n', nonces_directory
    ])


def main():
    logger = logging.getLogger("mpunks-supervisor")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    thread_state_lock = threading.Lock()
    thread_state = {
        'recentlyFetchedInputs': None,
        'workerManagerInputs': None,
        'processes': []
    }

    def kill_workers():
        for p in thread_state['processes']:
            p.kill()
        thread_state['processes'] = []

    atexit.register(kill_workers)

    def inputs_fetcher(controller_uri, state):
        while True:
            with thread_state_lock:
                try:
                    resp = requests.get(f'{controller_uri}/mining-inputs').json()
                    status = resp['status']
                    if status != 'success':
                        raise Exception(f'Received invalid status in response: {resp}')

                    state['recentlyFetchedInputs'] = resp['payload']
                    logger.info('Successfully fetched and updated mining inputs')
                    logger.info(state)
                except Exception as e:
                    logger.error(f'Error fetching inputs: {e}')
                    traceback.print_stack()

            time.sleep(5)

    def worker_manager(state):
        while True:
            with thread_state_lock:
                if json.dumps(state['workerManagerInputs']) != json.dumps(state['recentlyFetchedInputs']):
                    logger.info("Inputs diff detected. Re-spawning workers...")
                    kill_workers()

                    recently_fetched_inputs = state['recentlyFetchedInputs']
                    last_mined_assets = recently_fetched_inputs['lastMinedAssets']
                    sender_address = recently_fetched_inputs['senderAddress']
                    difficulty_target = recently_fetched_inputs['difficultyTarget']

                    p = spawn_worker(sender_address, last_mined_assets, difficulty_target, VALID_NONCES_DIRECTORY)
                    state['processes'].append(p)

                    state['workerManagerInputs'] = recently_fetched_inputs

            time.sleep(1)

    def work_submitter(controller_uri):
        while True:
            try:
                nonces = set(map(str.lower, os.listdir(VALID_NONCES_DIRECTORY)))
                submitted_nonces = get_or_init_submitted_nonces()
                unsubmitted_nonces = nonces - submitted_nonces

                '''
                There are a few possible scenarios when submitting a nonce for work.
                1. The nonce is valid and a transaction is submitted.
                2. The nonce is valid and an error occurs.
                3. The nonce is invalid and an error occurs.
                
                For simplicity, this program does not currently handle retrying
                on error.
                '''

                for nonce_file_name in unsubmitted_nonces:
                    hexNonce = f'0x{nonce_file_name}'
                    resp = requests.get(f'{controller_uri}/submit-work?nonce={hexNonce}')
                    log_payload = {
                        'action': 'submitted_work',
                        'nonce': hexNonce,
                        'resp': resp.json()
                    }
                    logger.info(json.dumps(log_payload))
                    append_submitted_nonce(nonce_file_name)

            except Exception as e:
                logger.error(f'Error while watching for work to submit, or while submitting work: {e}')
                traceback.print_stack()

            time.sleep(1)

    inputs_fetcher_thread = threading.Thread(target=inputs_fetcher, args=(CONTROLLER_URI, thread_state), daemon=True)
    worker_manager_thread = threading.Thread(target=worker_manager, args=(thread_state,), daemon=True)
    work_submitter_thread = threading.Thread(target=work_submitter, args=(CONTROLLER_URI,), daemon=True)

    create_valid_nonces_directory()

    inputs_fetcher_thread.start()
    worker_manager_thread.start()
    work_submitter_thread.start()

    while True:
        time.sleep(0.3)


if __name__ == '__main__':
    main()
