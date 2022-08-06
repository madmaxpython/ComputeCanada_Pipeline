#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Jun 27 12:23:25 2022

@author: maximeteixeira
"""

import paramiko


class ComputeCanadaJob:
    def __init__(self, config, username, model_path):
        self.config = config

        self.username = username
        self.model_path = model_path
        self.ssh_connection()
        self.analyze()

    def ssh_connection(self):
        connection_state = False

        while not connection_state:

            self.password = str(input("Password : "))

            try:
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.client.connect(self.config['host'], self.config['port'], self.username, self.password)
                connection_state = True
                print('Connection established')

            except Exception as e:
                print(e, "Please, verify your password and retry")

    def analyze(self):
        print('\nMake sure that you have place all your video in the following folder: ')
        print('/home/{}/projects/def-cflores/python_envs/CPPmodel/videos \n'.format(self.username))
        print('To analyze a 20 min video of CPP, it takes around 10 min \n ')

        time = str(input("Estimated time needed (respect format: HH:MM:SS): "))

        JobName = str(input("Job Name: "))

        spec = ' --time=' + time

        if self.config['emailNotification']:
            spec += " --mail-user=" + str(self.config['emailUser'])

        self.client.exec_command("sbatch" + spec + " " + "/home/{}/projects/def-cflores/python_envs/First_job_cc/slurmdeeplodocus.slurm".format(self.username) + " " + JobName)

        print("Job sent")
