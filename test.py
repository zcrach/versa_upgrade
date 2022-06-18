import pexpect
import getpass
import json
import sys
import re
import time

from requests import session

global max_retry_timeout

prompt = "\$"

hostname = "172.16.102.1"
username = "admin"
password = "versa123"
max_retry_timeout = 5

def versa_find_attribute(command_output, matching_string):
    variable_get = re.findall(r"[\n\r].*" + matching_string + "\s*([^\n\r\t]*)", command_output)
    return variable_get[0]


def die(child, errstr):
    print(errstr)
    print(child.before, child.after)
    child.terminate()
    exit(1)

def versa_connect():
    start_time = time.time()
    while time.time() - start_time <= max_retry_timeout:
        print(time.time())
        print(start_time)
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30)
        session_callback = ch.expect([pexpect.TIMEOUT, pexpect.EOF, 'yes/no', 'assword:', 'Connection refused', prompt, ] )
        print(session_callback)
        if session_callback == 0:
            die(ch, 'ERROR!\nSSH timed out. Here is what SSH said:' )
        elif session_callback == 1:
            die(ch, 'ERROR!\nSSH timed out. Here is what SSH said:' )
        elif session_callback == 2:
            ch = pexpect.spawn(f'ssh {username}@{hostname}')
            ch.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
            ch.sendline(password)
            ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
            ch.sendline('vsh details') 
            ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
            output = ch.before.decode()
            ch.sendline('exit')
            serial_number = versa_find_attribute(output, "Serial number")
            release = versa_find_attribute(output, "Release")
            print(serial_number)
            print(release)
            break
        else:
            time.sleep(0.5)
            break

    else:
        return False

def main():
    if not versa_connect():
        print("Failed")
    else:
        print("Successful")

if __name__ == '__main__':
    main()

