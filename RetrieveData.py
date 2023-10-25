import sys
import json
from pathlib import Path
from tkinter import Tk, filedialog
from distutils.util import strtobool
from GlobusTransfer import GlobusSession
from utils import YAMLReader

SCRIPT_PATH = str(Path(__file__).parent)

config = YAMLReader(SCRIPT_PATH)

LAPTOP_ID = config['ID']["user"]

CLIENT_ID = config['ID']["client"]

COMPUTECANADA_ENDPOINT_ID = config['ID']["endpoint"]

SCOPES = config["scopes"].replace('ENDPOINT_ID', COMPUTECANADA_ENDPOINT_ID)

REDIRECT_URL = config["redirect_url"]

globus = GlobusSession(CLIENT_ID, COMPUTECANADA_ENDPOINT_ID, REDIRECT_URL, SCOPES)

USERNAME = config['username']


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

    transfert_video = strtobool(input('Do you want the video(s) too (True/False): '))

    JOB_PATH = f"{config['TemporaryFolder'].replace('$USER', USERNAME)}/{JOB_NAME}"

    globus = GlobusSession(CLIENT_ID, COMPUTECANADA_ENDPOINT_ID, REDIRECT_URL, SCOPES)

    globus.TransferData(COMPUTECANADA_ENDPOINT_ID,
                        LAPTOP_ID,
                        f'{JOB_PATH}/csvfiles',
                        f"{DirectorySelector('Directory for the files')}/{JOB_NAME}",
                        True)

    if transfert_video:
        globus.TransferData(COMPUTECANADA_ENDPOINT_ID,
                            LAPTOP_ID,
                            f'{JOB_PATH}/csvfiles',
                            f"{DirectorySelector('Directory for the files')}/{JOB_NAME}",
                            True)
