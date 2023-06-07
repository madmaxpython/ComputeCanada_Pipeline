from GlobusTransfer import GlobusSession, FileSelector
from pathlib import Path
from utils import YAMLReader
from ScriptSSH import SSHClient
import json

SCRIPT_PATH = str(Path(__file__).parent)

if __name__ == "__main__":

    config = YAMLReader(SCRIPT_PATH)

    for parameter in config:
        if config[parameter] == '' and parameter != 'LastJobName':
            config[parameter] = input('{}? : '.format(parameter))

    LAPTOP_ID = config["user_id"]

    CLIENT_ID = config["client_id"]

    COMPUTECANADA_ENDPOINT_ID = config["endpoint_id"]

    SSHKEY_PATH = config['ssh_key_path']

    SCOPES = config["scopes"].replace('ENDPOINT_ID', COMPUTECANADA_ENDPOINT_ID)

    REDIRECT_URL = config["redirect_url"]

    globus = GlobusSession(CLIENT_ID, COMPUTECANADA_ENDPOINT_ID, REDIRECT_URL, SCOPES)

    USERNAME = config['username']

    MODEL_PATH = ""

    while MODEL_PATH == "":
        ASKED_MODEL = str(input("What behavior do you want to analyze?:\n "))

        try:
            MODEL_PATH = config['ModelList'][ASKED_MODEL].replace('$USER', USERNAME)

        except:
            print("\nModel doesn't exist, select one of the models below:")

            for MODEL_AVAILABLE in config['ModelList']:
                print("   - {}".format(MODEL_AVAILABLE))

    JOB_NAME = str(input("Job name: "))

    JOB_PATH = f"{config['TemporaryFolder'].replace('$USER', USERNAME)}/{JOB_NAME}"

    config["LastJobName"] = JOB_NAME
    RASP_PATH = f"{JOB_PATH}/rasp4"

    if not globus.checkDir(JOB_PATH):
        globus.mkdir(JOB_PATH)

    globus.mkdir(RASP_PATH)

    globus.TransferData(LAPTOP_ID,
                        COMPUTECANADA_ENDPOINT_ID,
                        FileSelector('Select video to analyze', True, [("Video files", ".mp4 .MOV .avi .h264")]),
                        RASP_PATH + '/',
                        False)

    ssh = SSHClient(config['host'],
                    USERNAME,
                    MODEL_PATH,
                    JOB_NAME,
                    SSHKEY_PATH,
                    config['script_folder'])

    ssh.connect()

    print('To analyze a 20 min video of CPP, it takes around 10 min\n ')

    time = str(input("Estimated time needed (respect format: HH:MM:SS): "))
    spec = ' --time=' + time

    ssh.execute_command(f"sbatch {spec} {f'/home/{USERNAME}/projects/def-cflores/Scripts/ScriptRasp/submit_job.sh'} {JOB_NAME} {MODEL_PATH.split('/')[-1]} rasp4")

    ssh.execute_command('sq')
    ssh.close()
