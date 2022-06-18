from email.mime import image
from posixpath import split
import pexpect
import getpass
import json
import sys
import re
import time

from requests import session

global max_retry_timeout, image_version

prompt = "\$"

hostname = "172.16.102.1"
username = "admin"
password = "versa123"
max_retry_timeout = 5

global image_filename, image_date, image_id, image_version
image_filename = "versa-flexvnf-20220420-131241-eca39c5-21.1.4-wsm.bin"
image_attributes = image_filename.split("-")
image_date = image_attributes[2]
image_id = image_attributes[4]
image_version = image_attributes[5]
#print(image_date)
#print(image_id)
#print(image_version)

def versa_find_attribute(command_output, matching_string):
    variable_get = re.findall(r"[\n\r].*" + matching_string + "\s*([^\n\r\t]*)", command_output)
    return variable_get[0]


def die(child, errstr):
    print(errstr)
    print(child.before, child.after)
    child.terminate()
    exit(1)

def versa_connect():
    """
    Connects to the device and gets the required attributes before we continue.
    Serial Number
    Current Image Version
    """
    start_time = time.time()
    while time.time() - start_time <= max_retry_timeout:
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
        session_callback = ch.expect([pexpect.TIMEOUT, pexpect.EOF, 'yes/no', 'assword:', 'Connection refused', prompt] )
        print(f"Currently using session_callback: {session_callback}")
        if session_callback == 0:
            die(ch, 'ERROR!\nSSH timed out. Here is what SSH said:' )
        elif session_callback == 1:
            die(ch, 'ERROR!\nSSH had an EOF error, here is what it said:' )
        elif session_callback == 2:
            ch.sendline('yes')
            ch.expect('assword:')
            ch.sendline(password)
            ch.expect(prompt)
        elif session_callback == 3:
            ch.sendline(password)
            ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
            output_ls = ch.before.decode()
            ch.sendline('vsh details') 
            ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
            output_vsh = ch.before.decode()
            ch.sendline('exit')
            print(output_vsh)
            if image_version in output_ls:
                print("success" + image_version)
            else:
                print("failed" + image_version)
            curr_conn_sn = versa_find_attribute(output_vsh, "Serial number")
            curr_conn_release_version = versa_find_attribute(output_vsh, "Release")
            curr_conn_release_id = versa_find_attribute(output_vsh, "Package id")
            curr_conn_release_date = versa_find_attribute(output_vsh, "Release date")
            print(curr_conn_release_id)
            print(curr_conn_release_date)
            print(curr_conn_release_version)
            print(curr_conn_sn)
            return True, curr_conn_release_version==image_version, 

        elif session_callback == 4:
            time.sleep(0.5)
        else:
            time.sleep(0.5)
            break
    else:
        return False

def main():
    versa_variables = versa_connect()
    print(versa_variables)
if __name__ == '__main__':
    main()

