from GlobusTransfer import GlobusSession, FileSelector
from ScriptSSH import SSHClient
from utils import YAMLReader
from pathlib import Path

SCRIPT_PATH = str(Path(__file__).parent)

if __name__ == "__main__":

    ###
    # Load useful variables for SSH connection and Globus File Transfer
    ###

    config = YAMLReader(SCRIPT_PATH)

    for parameter in config:
        if config[parameter] == '' and parameter != 'LastJobName':
            config[parameter] = input('{}? : '.format(parameter))

    LAPTOP_ID = config['ID']["user"]

    CLIENT_ID = config['ID']["client"]

    COMPUTECANADA_ENDPOINT_ID = config['ID']["endpoint"]

    SSHKEY_PATH = config['Folders']['ssh_key']

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

    while True:
        JOB_NAME = str(input("Job name: "))

        JOB_PATH = f"{config['Folders']['cc_user'].replace('$USER', USERNAME)}/{JOB_NAME}"
        if globus.checkDir(JOB_PATH):
            print("A project already has this name")

        else:
            break

    config["LastJobName"] = JOB_NAME

    ###
    # Authentication to Globus session, creation of project folder and transfer of files
    ###

    globus.mkdir(JOB_PATH)

    globus.mkdir(f"{JOB_PATH}/videos/")

    globus.TransferData(LAPTOP_ID,
                        COMPUTECANADA_ENDPOINT_ID,
                        FileSelector('Select video to analyze', True, [("Video files", ".mp4 .avi .h264")]),
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
                    config['Folders']['cc_script'])

    ssh.connect()
    print('To analyze a 20-min CPP video, it takes around 10 min\n ')
    ssh.submit_analysis()
    ssh.close()
