from GlobusTransfer import TransferGlobus
from pathlib import Path
import json
from connectcc import ComputeCanadaJob

script_path = str(Path(__file__).parent)

with open(script_path + '/config.txt', "r") as config_file:
    config = json.loads(config_file.read())

REDIRECT_URI = "https://auth.globus.org/v2/web/auth-code"

SCOPES = "urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/a1713da6-098f-40e6-b3aa-034efe8b6e5b/data_access]"

LAPTOP_ID = config["user_id"]

CLIENT_ID = config["client_id"]

COMPUTECANADA_ENDPOINT_ID = config["computecanada_id"]

USERNAME = config['username']

DESTINATION_FOLDER = config['DestinationFolder'].replace('$USER',USERNAME)

DEEPLODOCUS_FOLDER = config['DeeplodocusFolder'].replace('$USER',USERNAME)


if __name__ == "__main__":

    for parameter in config:
        if config[parameter] == '':
            config[parameter] = input('{}? : '.format(parameter))

    MODEL_PATH = ""

    while MODEL_PATH == "":
        ASKED_MODEL = str(input("What behavior do you want to analyze? (only CPP for now...) "))

        try:
            MODEL_PATH = config['ModelList'][ASKED_MODEL].replace('$USER',USERNAME)

        except:
            print("\nModel doesn't exist, select one of the models below:")

            for MODEL_AVAILABLE in config['ModelList']:
                print("   - {}".format(MODEL_AVAILABLE))

    TransferGlobus(LAPTOP_ID,
                   CLIENT_ID,
                   COMPUTECANADA_ENDPOINT_ID,
                   REDIRECT_URI,
                   SCOPES,
                   DESTINATION_FOLDER
                   )

    JOB_NAME = str(input("Job name: "))

    JOB_PATH = config['TemporaryFolder'].replace('$USER',USERNAME) +'/'+ JOB_NAME

    ComputeCanadaJob(config, USERNAME, MODEL_PATH, JOB_PATH, DEEPLODOCUS_FOLDER, DESTINATION_FOLDER, JOB_NAME)
