import sys
import json
from pathlib import Path
from tkinter import Tk, filedialog
from distutils.util import strtobool
from globus_sdk import NativeAppAuthClient, TransferClient, TransferData, RefreshTokenAuthorizer
from globus_sdk.exc import GlobusAPIError
from GlobusTransfer import load_tokens_from_file, do_native_app_authentication, save_tokens_to_file,\
    update_tokens_file_on_refresh


SCRIPT_PATH = str(Path(__file__).parent)

with open(SCRIPT_PATH + '/config.txt', "r") as config_file:
    config = json.loads(config_file.read())

TOKEN_FILE = SCRIPT_PATH + "/refresh-tokens.json"

LAPTOP_ID = config["user_id"]

CLIENT_ID = config["client_id"]

COMPUTECANADA_ENDPOINT_ID = config["computecanada_id"]
USERNAME=config['username']


SCOPES = f"urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/{COMPUTECANADA_ENDPOINT_ID}/data_access]"

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



def Transfer(JOB_NAME, t_videos=False):
    """
   Transfer selected files with FileSelector() to DESTINATION_FOLDER
   and wait for the transfer to be completed
   """
    tokens = None
    try:
        # if we already have tokens, load and use them
        tokens = load_tokens_from_file(TOKEN_FILE)
    except:
        pass

    if not tokens:
        # if we need to get tokens, start the Native App authentication process
        tokens = do_native_app_authentication(CLIENT_ID, REDIRECT_URI, SCOPES)
        try:
            save_tokens_to_file(TOKEN_FILE, tokens)
        except:
            pass

    transfer_tokens = tokens["transfer.api.globus.org"]
    auth_client = NativeAppAuthClient(client_id=CLIENT_ID)

    authorizer = RefreshTokenAuthorizer(
        transfer_tokens["refresh_token"],
        auth_client,
        access_token=transfer_tokens["access_token"],
        expires_at=transfer_tokens["expires_at_seconds"],
        on_refresh=update_tokens_file_on_refresh, )

    transfer = TransferClient(authorizer=authorizer)
    try:
        transfer.endpoint_autoactivate(LAPTOP_ID)
    except GlobusAPIError as ex:
        print(ex)
        if ex.http_status == 401:
            sys.exit(
                "Refresh token has expired. "
                "Please delete refresh-tokens.json and try again."
            )
        else:
            raise ex

    tdata = TransferData(transfer, COMPUTECANADA_ENDPOINT_ID,
                         LAPTOP_ID,
                         label="File Transfer",
                         sync_level="checksum")

    DESTINATION_FOLDER = DirectorySelector("Directory to transfer files")
    if JOB_NAME == '':
        JOB_NAME = config["LastJobName"]

    JOB_PATH = f"{config['TemporaryFolder'].replace('$USER', USERNAME)}/{JOB_NAME}"

    tdata.add_item(f'{JOB_PATH}/csvfiles', f"{DESTINATION_FOLDER}/{JOB_NAME}/csvfiles", recursive=True)

    if t_videos:
        tdata.add_item(f'{JOB_PATH}/videos', f"{DESTINATION_FOLDER}/{JOB_NAME}/videofiles", recursive=True)

    transfer_result = transfer.submit_transfer(tdata)
    print("_____________________________________________________________")
    print("Transferring your file to Compute Canada cluster")
    print("From: ",JOB_PATH)
    print("To: ", DESTINATION_FOLDER)

    print("task_id =", transfer_result["task_id"])
    print('Files in transfer')
    while not transfer.task_wait(transfer_result["task_id"], timeout=5):
        pass

    print("Task completed")
    print("_____________________________________________________________")


if __name__ == '__main__':
    JOBNAME= str(input('Job Name (empty if it is last job): '))
    T_VIDEO = strtobool(input('Do you want the video(s) too (True/False): '))
    print(T_VIDEO, type(T_VIDEO))
    Transfer(JOBNAME, T_VIDEO)
