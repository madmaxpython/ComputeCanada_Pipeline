from GlobusTransfer import GlobusSession, FileSelector
from ScriptSSH import SSHClient
from pathlib import Path
import json

SCRIPT_PATH = str(Path(__file__).parent)

with open(SCRIPT_PATH + '/config.txt', "r") as config_file:
    config = json.loads(config_file.read())

if __name__ == "__main__":

    ###
    # Load useful variables for SSH connection and Globus File Transfer
    ###

    for parameter in config:
        if config[parameter] == '' and parameter != 'LastJobName':
            config[parameter] = input('{}? : '.format(parameter))

    LAPTOP_ID = config["user_id"]

    CLIENT_ID = config["client_id"]

    COMPUTECANADA_ENDPOINT_ID = config["computecanada_id"]

    SSHKEY_PATH = config['ssh_key_path']

    SCOPES = f"urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/{COMPUTECANADA_ENDPOINT_ID}/data_access] "

    REDIRECT_URI = "https://auth.globus.org/v2/web/auth-code"

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

    config["LastJobName"] = JOB_NAME

    strconfig = json.dumps(config)

    with open(SCRIPT_PATH + '/config.txt', 'w') as file:
        file.write(strconfig)

    JOB_PATH = f"{config['TemporaryFolder'].replace('$USER', USERNAME)}/{JOB_NAME}"

    ###
    # Authentication to Globus session, creation of project folder and transfer of files
    ###

    globus = GlobusSession(CLIENT_ID, COMPUTECANADA_ENDPOINT_ID, REDIRECT_URI, SCOPES)

    globus.mkdir(JOB_PATH)

    globus.mkdir(f"{JOB_PATH}/videos/")

    globus.TransferData(LAPTOP_ID,
                        COMPUTECANADA_ENDPOINT_ID,
                        FileSelector('Select video to analyze', True, [("Video files", ".mp4 .MOV .avi .h264")]),
                        f"{JOB_PATH}/videos/",
                        False
                        )

    ###
    # Establish Secure Shell (SSH) communication and execution submission of job (using sbatch)
    ###

    ssh = SSHClient(config['host'],
                    USERNAME,
                    MODEL_PATH,
                    JOB_NAME,
                    SSHKEY_PATH,
                    config['script_folder'])

    ssh.connect()
    ssh.submit_analysis()
    ssh.close()
