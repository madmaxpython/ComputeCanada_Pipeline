import paramiko


class SSHClient:
    def __init__(self, hostname, username, model_path, job_name, private_key_path, script_path):
        self.hostname = hostname
        self.username = username
        self.script_path = script_path
        self.model_name = model_path.split('/')[-1]
        self.job_name = job_name
        self.private_key_path = private_key_path
        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            private_key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
            self.client.connect(self.hostname, username=self.username, pkey=private_key)
            print("Connected to", self.hostname)

        except paramiko.AuthenticationException:
            print("Failed to connect to", self.hostname, "- Invalid credentials.")

        except paramiko.SSHException as ssh_exception:
            print("Failed to connect to", self.hostname, "-", str(ssh_exception))

    def execute_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode()
        errors = stderr.read().decode()

        if output:
            print(output)
        if errors:
            print("Errors:")
            print(errors)

    def submit_analysis(self):
        time = str(input("Estimated time needed (respect format: HH:MM:SS): "))
        spec = ' --time=' + time

        self.execute_command(
            "sbatch" + spec + " " + self.script_path + "/submit_job.sh" + " " + self.job_name + ' ' + self.model_name)

        self.execute_command('sq')

    def close(self):
        self.client.close()
        print("Disconnected from", self.hostname)
