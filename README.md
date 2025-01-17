# ComputeCanada_Pipeline
Pipeline between user machine and compute canada, using globus.

#Setting up Config.yaml file

Folders:
cc_script: <em>Folder containing the script to execute for analysis</em>  
  cc_user: <em>User's personal space, $USER will be remplace by user name (ex:/home/$USER/projects/sponsor/$USER)</em>  
  ssh_key: <em>path to ssh key (id_rsa)</em>  
ID:  
  client: 
  endpoint: 
  user: 
LastJobName: 2024_09_05_Test_piepline_SIT
ModelList:
  model: model_path
host: narval.computecanada.ca
port: 22
redirect_url: https://auth.globus.org/v2/web/auth-code
scopes: urn:globus:auth:scope:transfer.api.globus.org:all[*https://auth.globus.org/scopes/ENDPOINT_ID/data_access]
username: maxtex
