import json
import sys
import webbrowser
from tkinter import Tk, filedialog

from globus_sdk import NativeAppAuthClient, TransferClient, TransferData, RefreshTokenAuthorizer
from globus_sdk.exc import GlobusAPIError

from utils import is_remote_session
from pathlib import Path


def FileSelector(TITLE, MULTIPLEFILES, FILETYPES):
    import platform
    """
    Open a file dialog window to select files to transfer
    return: a list of files directory
    """
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilenames(title=TITLE, multiple=MULTIPLEFILES, filetypes=FILETYPES)

    if platform.system() == 'Windows':
        import re
        print("Windows user detected")
        file_path = tuple([re.sub(r'(:)/', r'\1', path) for path in file_path])
    return file_path


class GlobusSession:
    def __init__(self,
                 CLIENT_ID,
                 COMPUTECANADA_ENDPOINT_ID,
                 REDIRECT_URI,
                 SCOPES):

        self.SCRIPT_PATH = str(Path(__file__).parent)
        self.TOKEN_FILE = self.SCRIPT_PATH + "/refresh-tokens.json"

        self.CLIENT_ID = CLIENT_ID
        self.COMPUTECANADA_ENDPOINT_ID = COMPUTECANADA_ENDPOINT_ID
        self.REDIRECT_URI = REDIRECT_URI
        self.SCOPES = SCOPES
        self.transfer_client = self.get_transfer_client()

    @staticmethod
    def load_tokens_from_file(filepath):
        """Load a set of saved tokens."""
        with open(filepath, "r") as f:
            tokens = json.load(f)
        return tokens

    @staticmethod
    def save_tokens_to_file(filepath, tokens):
        """Save a set of tokens for later use."""
        with open(filepath, "w") as f:
            json.dump(tokens, f)

    def update_tokens_file_on_refresh(self, token_response):
        """
        Callback function passed into the RefreshTokenAuthorizer.
        Will be invoked any time a new access token is fetched.
        """
        self.save_tokens_to_file(self.TOKEN_FILE, token_response.by_resource_server)

    @staticmethod
    def do_native_app_authentication(client_id, redirect_uri, SCOPES):
        """
        Does a Native App authentication flow and returns a
        dict of tokens keyed by service name.
        """
        client = NativeAppAuthClient(client_id=client_id)
        client.oauth2_start_flow(requested_scopes=SCOPES, redirect_uri=redirect_uri, refresh_tokens=True)
        url = client.oauth2_get_authorize_url()
        print("Native App Authorization URL: \n{}".format(url))

        if not is_remote_session():
            webbrowser.open(url, new=1)

        auth_code = input("Enter the auth code: ").strip()
        token_response = client.oauth2_exchange_code_for_tokens(auth_code)

        # return a set of tokens, organized by resource server name
        return token_response.by_resource_server

    def get_transfer_client(self):
        tokens = None
        try:
            # if we already have tokens, load and use them
            tokens = self.load_tokens_from_file(self.TOKEN_FILE)
        except:
            pass

        if not tokens:
            # if we need to get tokens, start the Native App authentication process
            tokens = self.do_native_app_authentication(self.CLIENT_ID, self.REDIRECT_URI, self.SCOPES)
            try:
                self.save_tokens_to_file(self.TOKEN_FILE, tokens)
            except:
                pass

        transfer_tokens = tokens["transfer.api.globus.org"]
        auth_client = NativeAppAuthClient(client_id=self.CLIENT_ID)

        authorizer = RefreshTokenAuthorizer(
            transfer_tokens["refresh_token"],
            auth_client,
            access_token=transfer_tokens["access_token"],
            expires_at=transfer_tokens["expires_at_seconds"],
            on_refresh=self.update_tokens_file_on_refresh, )

        transfer = TransferClient(authorizer=authorizer)
        try:
            transfer.endpoint_autoactivate(self.COMPUTECANADA_ENDPOINT_ID)
        except GlobusAPIError as ex:
            print(ex)
            if ex.http_status == 401:
                sys.exit(
                    "Refresh token has expired. "
                    "Please delete refresh-tokens.json and try again."
                )
            else:
                raise ex

        return transfer

    def checkDir(self, PATH_MKDIR):
        """
        Check if a directory exist in the endpoint
        """
        try:
            self.transfer_client.operation_ls(endpoint_id=self.COMPUTECANADA_ENDPOINT_ID, path=PATH_MKDIR)
            return True
        except GlobusAPIError:
            return False

    def mkdir(self, PATH_MKDIR):
        """
        Make a directory in the endpoint if it doesn't exist yet
        """

        if self.checkDir(PATH_MKDIR):
            print(f"{PATH_MKDIR} already exists")
        else:
            self.transfer_client.operation_mkdir(self.COMPUTECANADA_ENDPOINT_ID, PATH_MKDIR)
        print(f'{PATH_MKDIR} was created')

    def TransferData(self,
                     SOURCE_ENDPOINT_ID,
                     DESTINATION_ENDPOINT_ID,
                     SOURCE_FOLDER,
                     DESTINATION_FOLDER,
                     IS_A_FOLDER):

        tdata = TransferData(self.transfer_client, SOURCE_ENDPOINT_ID,
                             DESTINATION_ENDPOINT_ID,
                             label="File Transfer",
                             sync_level="checksum")
        if IS_A_FOLDER:
            tdata.add_item(SOURCE_FOLDER, DESTINATION_FOLDER + '/' + SOURCE_FOLDER.split('/')[-1],
                           recursive=IS_A_FOLDER)

        if not IS_A_FOLDER:
            for file in SOURCE_FOLDER:
                tdata.add_item(file, DESTINATION_FOLDER + file.split('/')[-1], recursive=IS_A_FOLDER)

        transfer_result = self.transfer_client.submit_transfer(tdata)

        print("_____________________________________________________________")
        print("Transferring your file(s)")
        print('From: ', SOURCE_FOLDER)
        print('To: ', DESTINATION_FOLDER)
        print("\ntask_id =", transfer_result["task_id"])
        print('Files in transfer')

        while not self.transfer_client.task_wait(transfer_result["task_id"], timeout=1200, polling_interval=12):
            pass

        print("Task completed")
        print("_____________________________________________________________")