#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 13:21:38 2022

@author: maximeteixeira
"""
import webbrowser
from globus_sdk import AccessTokenAuthorizer, NativeAppAuthClient, TransferClient, TransferData
from GlobusTransfer import TransferGlobus
from pathlib import Path
import paramiko

import json
from utils import enable_requests_logging, is_remote_session
from connectcc import ComputeCanadaJob


script_path = str(Path(__file__).parent)


with open(script_path+'/config.txt', "r") as config_file:
    config = json.loads(config_file.read())
    

REDIRECT_URI = "https://auth.globus.org/v2/web/auth-code"

SCOPES = "urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/a1713da6-098f-40e6-b3aa-034efe8b6e5b/data_access]"

LAPTOP_ID= config["user_id"]

CLIENT_ID = config["client_id"]

COMPUTECC_ENDPOINT_ID = config["computecanada_id"]


if __name__ == "__main__":
    
    for parameters in config:
       if config[parameters] =='':
           config[parameters]=input('{}? : '.format(parameters))
        
    
    USERNAME=config['username']
    
    MODEL_PATH=""

    while MODEL_PATH=="":
        ASKED_MODEL = str(input("Which model: "))
        
        try:
            MODEL_PATH=config['ModelList'][ASKED_MODEL]
            
        except :
            print('\nModel dont exist, select on of the model bellow:')
            
            for MODEL_AVAILABLE in config['ModelList']:
                print("   - {}".format(MODEL_AVAILABLE))
            
    TransferGlobus(USERNAME,
                   LAPTOP_ID,
                   CLIENT_ID,
                   COMPUTECC_ENDPOINT_ID,
                   REDIRECT_URI,
                   SCOPES, 
                   config['SourceFolder'],
                   MODEL_PATH
                   )
    
    ComputeCanadaJob(config, USERNAME)
    