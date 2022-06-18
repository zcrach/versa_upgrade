import pexpect
import getpass
import sys

prompt = "\$"

hostname = "172.16.102.1"
username = "admin"
password = "versa123"


ch = pexpect.spawn(f'ssh {username}@{hostname}')
#ch.logfile = sys.stdout.buffer
ch.expect('assword:')
ch.sendline(password)
ch.expect(prompt)
ch.sendline('vsh details | grep -o "Serial number.*"') 
ch.expect(prompt)
output = ch.before.decode('utf-8').splitlines()
ch.sendline('exit')
#print(output)
line_number = 0
for line in output:
    print(line)
