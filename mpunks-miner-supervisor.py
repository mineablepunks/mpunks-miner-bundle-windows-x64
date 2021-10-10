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
DEVICE_LIST_STRING = default_config.get("DeviceList") or "0"
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


def spawn_worker(sender_bits, last_mined_assets, difficulty_target, nonces_directory, device_id):
    if not os.path.exists(WORKER_EXECUTABLE_PATH):
        raise Exception(f"Worker Executable Path '{WORKER_EXECUTABLE_PATH}' not found!")

    # The worker will start at a random nonce between 0 and 2^64
    return subprocess.Popen([
        WORKER_EXECUTABLE_PATH,
        '-a', sender_bits,
        '-l', last_mined_assets,
        '-d', difficulty_target,
        '-n', nonces_directory,
        '-x', device_id
    ])


class NonceStatus:
    FAILS_DIFFICULTY_TEST = "FAILS_DIFFICULTY_TEST"
    PRODUCES_EXISTING_MPUNK = "PRODUCES_EXISTING_MPUNK"
    PRODUCES_EXISTING_OG_PUNK = "PRODUCES_EXISTING_OG_PUNK"
    VALID = "VALID"


def main():
    logger = logging.getLogger("mpunks-supervisor")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    thread_state_lock = threading.Lock()
    thread_state = {
        'recentlyFetchedInputs': None,
        'workerManagerInputs': None,
        'processes': [],
        'exit': False
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

                    device_ids = DEVICE_LIST_STRING.split(',')
                    for device_id in device_ids:
                        p = spawn_worker(
                            sender_address,
                            last_mined_assets,
                            difficulty_target,
                            VALID_NONCES_DIRECTORY,
                            device_id
                        )

                        time.sleep(3)

                        process_alive = (p.poll() is None)
                        if not process_alive:
                            logger.fatal(f'Failed to launch worker with device_id {device_id}. Exiting...')
                            state['exit'] = True
                            break

                        state['processes'].append(p)

                    state['workerManagerInputs'] = recently_fetched_inputs

            time.sleep(1)

    def work_submitter(controller_uri):
        while True:
            try:
                nonces = set(map(str.lower, os.listdir(VALID_NONCES_DIRECTORY)))
                submitted_nonces = get_or_init_submitted_nonces()
                unsubmitted_nonces = nonces - submitted_nonces

                for nonce_file_name in unsubmitted_nonces:
                    hex_nonce = f'0x{nonce_file_name}'
                    resp = requests.post(f'{controller_uri}/submit-work?nonce={hex_nonce}')
                    json_data = resp.json()
                    req_status = json_data['status']

                    if req_status == "success":
                        append_submitted_nonce(nonce_file_name)
                    else:
                        payload = json_data['payload']
                        if 'nonceStatus' in payload:
                            nonce_status = payload['nonceStatus']
                            if nonce_status != NonceStatus.VALID:
                                # Only add to submitted nonces if the nonce wasn't valid
                                append_submitted_nonce(nonce_file_name)

                    log_payload = {
                        'action': 'submitted_work',
                        'nonce': hex_nonce,
                        'resp': resp.json()
                    }
                    logger.info(json.dumps(log_payload))

            except Exception as e:
                logger.error(f'Error while watching for work to submit, or while submitting work: {e}')
                traceback.print_stack()

            time.sleep(5)

    inputs_fetcher_thread = threading.Thread(target=inputs_fetcher, args=(CONTROLLER_URI, thread_state), daemon=True)
    worker_manager_thread = threading.Thread(target=worker_manager, args=(thread_state,), daemon=True)
    work_submitter_thread = threading.Thread(target=work_submitter, args=(CONTROLLER_URI,), daemon=True)

    create_valid_nonces_directory()

    inputs_fetcher_thread.start()
    worker_manager_thread.start()
    work_submitter_thread.start()

    while True:
        if thread_state['exit']:
            sys.exit(1)
        time.sleep(0.3)


if __name__ == '__main__':
    main()
