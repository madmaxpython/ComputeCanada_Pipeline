import paramiko

class ComputeCanadaJob:
    def __init__(self, config, username, model_path, job_path, deeplodocus_path, destination_folder, job_name):
        self.config = config
        self.username = username
        self.model_path = model_path
        self.job_path = job_path
        self.deeplodocus_path = deeplodocus_path
        self.destination_folder = destination_folder
        self.job_name = job_name
        self.model_name = self.model_path.split('/')[-1]
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
        print('\nMake sure that you have placed all your videos in the following folder: ')
        print('/home/{}/projects/def-cflores/{}/videos_to_analyze \n'.format(self.username,self.username))
        print('To analyze a 20 min video of CPP, it takes around 10 min \n ')

        time = str(input("Estimated time needed (respect format: HH:MM:SS): "))

        spec = ' --time=' + time

        if self.config['emailNotification']:
            spec += " --mail-user=" + str(self.config['emailUser'])

        self.client.exec_command("mkdir" + " " + self.job_path)

        self.client.exec_command("cp -r " + self.model_path + " " + self.job_path)

        self.client.exec_command("cp -r " + self.deeplodocus_path + " " + self.job_path)

        self.client.exec_command("cp -r " + self.destination_folder + " " + self.job_path + '/' + self.model_name + '/videos')

        self.client.exec_command("sbatch" + spec + " " + self.job_path + "Deeplodocus/bash_deeplodocus.slurm" + " " + self.job_name + ' ' + self.model_name)

        print("Job sent")
