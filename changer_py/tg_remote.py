import paramiko



def ssh(host, username, password, command):
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password, allow_agent=False, look_for_keys=False)
    _stdin, _stdout,_stderr = client.exec_command(command)
    return _stdout.read().decode()
    client.close()
