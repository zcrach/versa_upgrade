import pexpect
import getpass
import json
import sys
import re

prompt = "\$"

hostname = "172.16.102.1"
username = "admin"
password = "versa123"


def versa_find_attribute(command_output, matching_string):
    variable_get = re.findall(r"[\n\r].*" + matching_string + "\s*([^\n\r\t]*)", command_output)
    return variable_get[0]

def versa_connect()
    start_time = time.time()
    while time.time() - start_time <= max_retry_timeout:
ch = pexpect.spawn(f'ssh {username}@{hostname}')
#ch.logfile = sys.stdout.buffer
ch.expect('assword:')
ch.sendline(password)
ch.expect(prompt)
ch.sendline('vsh details') 
ch.expect(prompt)
output = ch.before.decode()
ch.sendline('exit')
serial_number = versa_find_attribute(output, "Serial number")
release = versa_find_attribute(output, "Release")
print(serial_number)
print(release)

def main():
    

if __name__ == '__main__':
    main()