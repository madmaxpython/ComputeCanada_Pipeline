#!/usr/bin/env python

import json
import sys
import webbrowser
from globus_sdk import AccessTokenAuthorizer, NativeAppAuthClient, TransferClient, TransferData, RefreshTokenAuthorizer
from utils import enable_requests_logging, is_remote_session
from globus_sdk.exc import GlobusAPIError

TOKEN_FILE = "refresh-tokens.json"

def load_tokens_from_file(filepath):
    """Load a set of saved tokens."""
    with open(filepath, "r") as f:
        tokens = json.load(f)
    return tokens

def save_tokens_to_file(filepath, tokens):
    """Save a set of tokens for later use."""
    with open(filepath, "w") as f:
        json.dump(tokens, f)

def update_tokens_file_on_refresh(token_response):
    """
    Callback function passed into the RefreshTokenAuthorizer.
    Will be invoked any time a new access token is fetched.
    """
    save_tokens_to_file(TOKEN_FILE, token_response.by_resource_server)

def do_native_app_authentication(client_id, redirect_uri, SCOPES, requested_scopes=None):
    """
    Does a Native App authentication flow and returns a
    dict of tokens keyed by service name.
    """
    client = NativeAppAuthClient(client_id=client_id)
    client.oauth2_start_flow(requested_scopes=SCOPES, redirect_uri=redirect_uri,refresh_tokens=True)
    url = client.oauth2_get_authorize_url()
    print("Native App Authorization URL: \n{}".format(url))

    if not is_remote_session():
        webbrowser.open(url, new=1)

    auth_code = input("Enter the auth code: ").strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

    # return a set of tokens, organized by resource server name
    return token_response.by_resource_server


def TransferGlobus(username,
                   LAPTOP_ID,
                   CLIENT_ID,
                   COMPUTECC_ENDPOINT_ID,
                   REDIRECT_URI,
                   SCOPES,
                   SOURCE_FOLDER,
                   DESTINATION_FOLDER):
   """
   Transfer files contains from SOURCE_FOLDER to DESTINATION_FOLDER
   and wait  the transfer to be completed 
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
       on_refresh=update_tokens_file_on_refresh,)

   transfer = TransferClient(authorizer=authorizer)
   try:
       transfer.endpoint_autoactivate(COMPUTECC_ENDPOINT_ID)
   except GlobusAPIError as ex:
       print(ex)
       if ex.http_status == 401:
           sys.exit(
               "Refresh token has expired. "
               "Please delete refresh-tokens.json and try again."
           )
       else:
           raise ex

   tdata = TransferData(transfer, LAPTOP_ID,
                               COMPUTECC_ENDPOINT_ID,
                               label="File Transfer",
                               sync_level="checksum")
   
   tdata.add_item(SOURCE_FOLDER, DESTINATION_FOLDER,
              recursive=True)
   
   transfer_result = transfer.submit_transfer(tdata)
   print("Transfering your file to Compute Canada cluster")
   print("task_id =", transfer_result["task_id"])
   
   while not transfer.task_wait(transfer_result["task_id"], timeout=5):
       print("Task {0} is running"
             .format(transfer_result["task_id"]))
       
   print("Task completed")
     
