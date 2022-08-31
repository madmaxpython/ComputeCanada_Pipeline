import sys
import json
from pathlib import Path
from tkinter import Tk, filedialog
from distutils.util import strtobool
from GlobusTransfer import TransferGlobus

SCRIPT_PATH = str(Path(__file__).parent)

with open(SCRIPT_PATH + '/config.txt', "r") as config_file:
    config = json.loads(config_file.read())

LAPTOP_ID = config["user_id"]

CLIENT_ID = config["client_id"]

COMPUTECANADA_ENDPOINT_ID = config["computecanada_id"]

USERNAME = config['username']

SCOPES = f"urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/{COMPUTECANADA_ENDPOINT_ID}/data_access] "

REDIRECT_URI = "https://auth.globus.org/v2/web/auth-code"


def DirectorySelector(TITLE):
    """
    Open a file dialog window to select files to transfer
    return: a list of files directory
    """
    root = Tk()
    root.withdraw()
    file_path = filedialog.askdirectory(title=TITLE)
    return file_path


if __name__ == '__main__':

    JOB_NAME = str(input('Job Name (empty if it is last job): '))

    if JOB_NAME == '':
        JOB_NAME = config["LastJobName"]

    T_VIDEO = strtobool(input('Do you want the video(s) too (True/False): '))

    JOB_PATH = f"{config['TemporaryFolder'].replace('$USER', USERNAME)}/{JOB_NAME}"

    TransferGlobus(COMPUTECANADA_ENDPOINT_ID,
                   CLIENT_ID,
                   LAPTOP_ID,
                   REDIRECT_URI,
                   SCOPES,
                   f'{JOB_PATH}/csvfiles',
                   f"{DirectorySelector('Directory for the files')}/{JOB_NAME}",
                   True)

    if T_VIDEO:
        TransferGlobus(COMPUTECANADA_ENDPOINT_ID,
                       CLIENT_ID,
                       LAPTOP_ID,
                       REDIRECT_URI,
                       SCOPES,
                       f'{JOB_PATH}/videos',
                       f"{DirectorySelector('Directory for the files')}/{JOB_NAME}",
                       True)
