#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Jun 27 12:23:25 2022

@author: maximeteixeira
"""

import paramiko
import json
from pathlib import Path

def connection_login(config):
    if config['username'] =='':
        username = str(input("Username: "))
    else: 
        username=config['username']
    
    password =str(input("Password : "))
    return username, password

def RunJobComputeCC(username, config):
    connection_state = False
    while connection_state ==False:
    
        password = str(input("Password : "))
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(config['host'], config['port'], username, password)
            connection_state=True
        
        except Exception as e:
            print (e, "\nPlease, retry")
    
    print('\nMake sure that you have place all your video in the following folder: ')
    print('/home/[your_username]/projects/def-cflores/python_envs/CPPmodel/videos \n')
    print('To analyze a 20 min video of CPP, it takes around 10 min \n ')

    time = str(input("Estimated time needed (respect format: DD-HH:MM:SS): "))

    JobName= str(input("Job Name: "))

    spec=' --time='+time

    if config['emailNotification']==True:
        spec+=" --mail-user="+str(config['emailUser'])

    ssh.exec_command("cd /home/"+username+"/projects/def-cflores/python_envs/First_job_cc/")

    ssh.exec_command("sbatch"+spec+" /home/"+username+"/projects/def-cflores/python_envs/First_job_cc/slurmdeeplodocus.slurm "+ JobName)

    print("Job sent")
    
    