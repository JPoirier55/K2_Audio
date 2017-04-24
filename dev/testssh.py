import sshtunnel
import os
import paramiko

ssh = paramiko.SSHClient()
ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
ssh.connect('192.168.255.25', username='debian', password='temppwd')
sftp = ssh.open_sftp()
sftp.put('test.txt', '/home/debian/test.txt')
sftp.close()
ssh.close()
