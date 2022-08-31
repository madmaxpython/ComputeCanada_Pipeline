from GlobusTransfer import TransferGlobus, mkdirGlobus, FileSelector
from pathlib import Path
import json
import os
from connectcc import ComputeCanadaJob

SCRIPT_PATH = str(Path(__file__).parent)

with open(SCRIPT_PATH + '/config.txt', "r") as config_file:
    config = json.loads(config_file.read())

if __name__ == "__main__":

    for parameter in config:
        if config[parameter] == '':
            config[parameter] = input('{}? : '.format(parameter))

    LAPTOP_ID = config["user_id"]

    CLIENT_ID = config["client_id"]

    COMPUTECANADA_ENDPOINT_ID = config["computecanada_id"]

    SCOPES = f"urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/{COMPUTECANADA_ENDPOINT_ID}/data_access]"

    REDIRECT_URI = "https://auth.globus.org/v2/web/auth-code"

    USERNAME = config['username']

    MODEL_PATH = ""

    SCRIPT_FOLDER = config['script_folder']

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
                   True)

    TransferGlobus(LAPTOP_ID,
                   CLIENT_ID,
                   COMPUTECANADA_ENDPOINT_ID,
                   REDIRECT_URI,
                   SCOPES,
                   FileSelector('Select video to analyze', True, [("Video files", ".mp4 .MOV .avi")]),
                   os.path.join(JOB_PATH, MODEL_PATH.split('/')[-1], 'videos/'),
                   False
                   )
    TransferGlobus(COMPUTECANADA_ENDPOINT_ID,
                   CLIENT_ID,
                   COMPUTECANADA_ENDPOINT_ID,
                   REDIRECT_URI,
                   SCOPES,
                   [f"{SCRIPT_FOLDER.replace('$USER', USERNAME)}/submit_job.sh",
                    f"{SCRIPT_FOLDER.replace('$USER', USERNAME)}/requirements.txt",
                    f"{SCRIPT_FOLDER.replace('$USER', USERNAME)}/Deeplabcut_analysis.py"],
                   JOB_PATH+'/',
                   False)

    ComputeCanadaJob(config, USERNAME, MODEL_PATH, JOB_PATH, JOB_NAME)
