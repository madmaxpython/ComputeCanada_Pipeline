# ComputeCanada_Pipeline
Pipeline between user machine and compute canada, using globus.

#Setting up Config.yaml file

Folders:
cc_script: <em>Folder containing the script to execute for analysis</em>  
  cc_user: <em>User's personal space, $USER will be remplace by user name (ex:/home/$USER/projects/sponsor/$USER)</em>  
  ssh_key: <em>path to ssh key (id_rsa)</em>  
ID:  
  client: ce15da75-1dd2-49ee-b980-3871b7c6034f
  endpoint: a1713da6-098f-40e6-b3aa-034efe8b6e5b
  user: 832cb60a-6bdd-11ef-aae0-7d6f43498e7d
LastJobName: 2024_09_05_Test_piepline_SIT
ModelList:
  CPP_R: /home/$USER/projects/def-cflores/DLC_model/CPP
  EPM: /home/$USER/projects/def-cflores/DLC_model/ElevatedPlusMaze
  LocoNew: /home/$USER/projects/def-cflores/DLC_model/Locomotor-Max-2023-05-23
  Locomotor: /home/$USER/projects/def-cflores/DLC_model/LocomotorActivity
  SIT_Fiber: /home/$USER/projects/def-cflores/DLC_model/Fiberphotometry2-Erick-2024-08-15/
host: narval.computecanada.ca
port: 22
redirect_url: https://auth.globus.org/v2/web/auth-code
scopes: urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/ENDPOINT_ID/data_access]
username: maxtex
