from pexpect import pxssh
from email.mime import image
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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

def versa_parse_output(command_output, matching_string):
    variable_get = re.findall(r"[\n\r].*" + matching_string + "\s*([^\n\r\t]*)", command_output)
    return variable_get[0]


def die(child, errstr):
    print(errstr)
    print(child.before, child.after)
    child.terminate()
    exit(1)


def versa_get_attributes(ch):
    correct_image_exists = False
    image_check = False
    vsh_running = False
    #Initial login
    ch.sendline(password)
    ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
    #Check vsh status
    ch.sendline('vsh status')
    ch.expect(['admin:', pexpect.EOF, pexpect.TIMEOUT])
    ch.sendline(password)
    ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
    output_status = ch.before.decode()

    #Check package file
    ch.sendline('ls /home/versa/packages') 
    ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
    output_ls = ch.before.decode()

    #Check vsh details
    ch.sendline('vsh details') 
    ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
    output_vsh = ch.before.decode()
    ch.sendline('exit')

    if "Stopped" in output_status:
        vsh_running = False
    else:
        vsh_running = True

    if image_filename in output_ls:
        correct_image_exists = True
    else:
        correct_image_exists = False
    active_sn = versa_parse_output(output_vsh, "Serial number")
    active_version = versa_parse_output(output_vsh, "Release")
    active_id = versa_parse_output(output_vsh, "Package id")
    active_date = versa_parse_output(output_vsh, "Release date")

    if active_version == image_version and active_id == image_id and active_date == image_date:
        image_check = True
        return True, image_check, correct_image_exists, vsh_running
    else:
        image_check = False
        return False, image_check, correct_image_exists, vsh_running



def versa_connect():
    """
    Connects to the device and gets the required attributes before we continue.
    Serial Number
    Current Image Version
    """
    start_time = time.time()
    upgrade_required = True
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
            versa_attributes = versa_get_attributes(ch)
            print(versa_attributes[1])
            return True, versa_attributes[1], versa_attributes[2], versa_attributes[3]

        elif session_callback == 4:
            time.sleep(0.5)
        else:
            time.sleep(0.5)
            break
    else:
        return False

def main():
    versa_variables = versa_connect()
    #Versa_variables[0] = Login ok
    #Versa_variables[1] = Version OK
    #versa_variables[2] = Image file ok

    print(versa_variables)
if __name__ == '__main__':
    main()

