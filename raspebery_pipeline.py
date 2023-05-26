from GlobusTransfer import TransferGlobus, mkdirGlobus, FileSelector, checkDirGlobus
import os
from pathlib import Path
import json

import paramiko


class SSHClient:
    def __init__(self, hostname, username, model_path, job_path, job_name, private_key_path, rasp_folder):
        self.hostname = hostname
        self.username = username
        self.model_path = model_path
        self.model_name = self.model_path.split('/')[-1]
        self.job_path = job_path
        self.job_name = job_name
        self.rasp_folder = rasp_folder
        self.private_key_path = private_key_path
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            private_key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
            self.client.connect(self.hostname, username=self.username, pkey=private_key)
            print("Connected to", self.hostname)

        except paramiko.AuthenticationException:
            print("Failed to connect to", self.hostname, "- Invalid credentials.")

        except paramiko.SSHException as ssh_exception:
            print("Failed to connect to", self.hostname, "-", str(ssh_exception))

    def execute_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode()
        errors = stderr.read().decode()

        if output:
            print(output)
        if errors:
            print("Errors:")
            print(errors)

    def submit_analysis(self):
        print('\nMake sure that you have placed all your videos in the following folder: ')
        print('/home/{}/projects/def-cflores/{}/videos_to_analyze \n'.format(self.username, self.username))
        print('To analyze a 20 min video of CPP, it takes around 10 min \n ')

        time = str(input("Estimated time needed (respect format: HH:MM:SS): "))
        spec = ' --time=' + time

        self.execute_command(
            f"sbatch {spec} {self.job_path}/submit_job.sh {self.job_name} {self.model_name} {self.rasp_folder}")

        self.execute_command('sq')

    def close(self):
        self.client.close()
        print("Disconnected from", self.hostname)


SCRIPT_PATH = str(Path(__file__).parent)

with open(SCRIPT_PATH + '/config.txt', "r") as config_file:
    config = json.loads(config_file.read())

if __name__ == "__main__":

    for parameter in config:
        if config[parameter] == '' and parameter != 'LastJobName':
            config[parameter] = input('{}? : '.format(parameter))

    LAPTOP_ID = config["user_id"]

    CLIENT_ID = config["client_id"]

    COMPUTECANADA_ENDPOINT_ID = config["computecanada_id"]

    SCOPES = f"urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/{COMPUTECANADA_ENDPOINT_ID}/data_access] "

    REDIRECT_URI = "https://auth.globus.org/v2/web/auth-code"

    USERNAME = config['username']

    MODEL_PATH = ""

    SCRIPT_FOLDER = '/home/$USER/projects/def-cflores/Scripts/ScriptRasp'

    SSHKEY_PATH = config['ssh_key_path']

    while MODEL_PATH == "":
        ASKED_MODEL = str(input("What behavior do you want to analyze?:\n "))

        try:
            MODEL_PATH = config['ModelList'][ASKED_MODEL].replace('$USER', USERNAME)

        except:
            print("\nModel doesn't exist, select one of the models below:")

            for MODEL_AVAILABLE in config['ModelList']:
                print("   - {}".format(MODEL_AVAILABLE))

    JOB_NAME = str(input("Job name: "))

    config["LastJobName"] = JOB_NAME

    strconfig = json.dumps(config)

    with open(SCRIPT_PATH + '/config.txt', 'w') as file:
        file.write(strconfig)

    JOB_PATH = os.path.join(config['TemporaryFolder'].replace('$USER', USERNAME), JOB_NAME)
    RASP_PATH = os.path.join(JOB_PATH, 'rasp3')

    if not checkDirGlobus(CLIENT_ID, COMPUTECANADA_ENDPOINT_ID, REDIRECT_URI, SCOPES, JOB_PATH):
        mkdirGlobus(CLIENT_ID,
                    COMPUTECANADA_ENDPOINT_ID,
                    REDIRECT_URI,
                    SCOPES,
                    JOB_PATH)

        TransferGlobus(COMPUTECANADA_ENDPOINT_ID,
                       CLIENT_ID,
                       COMPUTECANADA_ENDPOINT_ID,
                       REDIRECT_URI,
                       SCOPES,
                       MODEL_PATH,
                       JOB_PATH,
                       True
                       )

        TransferGlobus(COMPUTECANADA_ENDPOINT_ID,
                       CLIENT_ID,
                       COMPUTECANADA_ENDPOINT_ID,
                       REDIRECT_URI,
                       SCOPES,
                       [f"{SCRIPT_FOLDER.replace('$USER', USERNAME)}/submit_job.sh",
                        f"{SCRIPT_FOLDER.replace('$USER', USERNAME)}/requirements.txt",
                        f"{SCRIPT_FOLDER.replace('$USER', USERNAME)}/Deeplabcut_analysis.py"],
                       JOB_PATH + '/',
                       False)
    elif not checkDirGlobus(CLIENT_ID, COMPUTECANADA_ENDPOINT_ID, REDIRECT_URI, SCOPES, os.path.join(JOB_PATH, config['ModelList'][ASKED_MODEL].split('/')[-1])):
        TransferGlobus(COMPUTECANADA_ENDPOINT_ID,
                       CLIENT_ID,
                       COMPUTECANADA_ENDPOINT_ID,
                       REDIRECT_URI,
                       SCOPES,
                       MODEL_PATH,
                       JOB_PATH,
                       True
                       )

        TransferGlobus(COMPUTECANADA_ENDPOINT_ID,
                       CLIENT_ID,
                       COMPUTECANADA_ENDPOINT_ID,
                       REDIRECT_URI,
                       SCOPES,
                       [f"{SCRIPT_FOLDER.replace('$USER', USERNAME)}/submit_job.sh",
                        f"{SCRIPT_FOLDER.replace('$USER', USERNAME)}/requirements.txt",
                        f"{SCRIPT_FOLDER.replace('$USER', USERNAME)}/Deeplabcut_analysis.py"],
                       JOB_PATH + '/',
                       False)

    mkdirGlobus(CLIENT_ID,
                COMPUTECANADA_ENDPOINT_ID,
                REDIRECT_URI,
                SCOPES,
                RASP_PATH)

    TransferGlobus(LAPTOP_ID,
                   CLIENT_ID,
                   COMPUTECANADA_ENDPOINT_ID,
                   REDIRECT_URI,
                   SCOPES,
                   FileSelector('Select video to analyze', True, [("Video files", ".mp4 .MOV .avi")]),
                   RASP_PATH+'/',
                   False
                   )

    ssh = SSHClient(config['host'], USERNAME, MODEL_PATH, JOB_PATH, JOB_NAME, SSHKEY_PATH, RASP_PATH)
    ssh.connect()
    ssh.submit_analysis()
    ssh.close()

