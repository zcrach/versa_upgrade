#Imports

from pexpect import pxssh
from email.mime import image
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os, sys, re, argparse, signal, time, base64, subprocess, pexpect, threading, struct, socket, datetime, getpass, smtplib


global hostname, username, password, image_location, image_filename, script_is_running, upgrade_status
image_filename = "versa-flexvnf-20220420-131241-eca39c5-21.1.4-wsm.bin"
#image_filename = "versa-flexvnf-20210604-182611-84d9ad4-21.1.3-wsm.bin"


image_location = '/home/versaupgrade/versa/' + image_filename
upgrade_status_test = "test"
hostname = "172.16.102.1"
username = "admin"
password = "versa123"

script_is_running = True

prompt = "@.*:~\$|:.* ~].* #"
cli_prompt = ".*cli>"
config_prompt = ".*%"

#Defines the login details



def connect(name="", max_retry_timeout=200):
    start_time = time.time()
    while time.time() - start_time <= max_retry_timeout:
        login_details = pxssh.pxssh()
        login_details.login(hostname, username, password, login_timeout=30)

        active_session = pexpect.spawn(f'ssh {username}@{hostname}', encoding='utf-8', timeout=60)
        active_session.logfile = sys.stdout
        #print(active_session.read())
        i = active_session.expect(['yes/no', 'assword:', 'Connection refused', prompt])
        if i == 0:
            active_session.sendline('yes')
            active_session.expect(["assword:", pexpect.EOF, pexpect.TIMEOUT])
            active_session.sendline(password)
            active_session.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
            break
        elif i == 1:
            active_session.sendline(password) #Error here
            active_session.expect(["$", pexpect.EOF, pexpect.TIMEOUT])
            break
        elif i == 2:
            time.sleep(0.5)
            break
        else:
            time.sleep(0.5)
            break
    
    if not name == "":
       print ("SSH session login to %s ( %s ) successful" % (hostname,name))
    output = active_session.before + active_session.after
    return active_session

def scp_image_filenames():
    try:
        cmd = f'sshpass -p {password} scp -o StrictHostKeyChecking=no {image_location} admin@{hostname}:/home/versa/packages/'
        output = subprocess.check_output(cmd, shell=True) 
        return True
    except:
        return False

def upgrade():
        list_of_globals = globals()
        list_of_globals['upgrade_status_test'] = "variable_reset"
        print(list_of_globals['upgrade_status_test'])
        active_session_cli = connect()
        if not active_session_cli:
            return False
        active_session_cli.sendline(password)
        active_session_cli.expect(["$", pexpect.EOF, pexpect.TIMEOUT])
        active_session_cli.sendline("cli")
        active_session_cli.expect(["cli>", pexpect.EOF, pexpect.TIMEOUT])
        active_session_cli.sendline(f"request system package upgrade {image_filename}")
        active_session_cli.expect(["[no,yes]", pexpect.EOF, pexpect.TIMEOUT])
        active_session_cli.sendline("yes")
        active_session_cli.expect(["cli>", pexpect.EOF, pexpect.TIMEOUT])
        output_installed = active_session_cli.before
        if "already installed" in output_installed:
            list_of_globals['upgrade_status_test'] = "upgrade_done"
            return True
        elif "Initiating upgrade" in output_installed:
            list_of_globals['upgrade_status_test'] = "upgrade_starting"
            return True
        else:
            list_of_globals['upgrade_status_test'] = "upgrade_failed"
            return False


def main():
    while script_is_running is True:
        if not scp_image_filenames():
            print ("ERROR: Unable to scp image_filename to device %s"%hostname)
        else:
            print ("SUCCESS: %s image_filename is copied to device %s"%(image_location, hostname))
            if not upgrade():
                print("Failed to upgrade")
            elif upgrade_status_test == "upgrade_starting":
                print("Successfully started upgrading of device, estimated time 20-30 minutes")
                time.sleep(600)
            elif upgrade_status_test == "upgrade_done":
                print("Upgrade is already done")
            else:
                print("No idea what happened")
                print("lets wait 10 minutes and try again")
                time.sleep(600)
                print(upgrade_status)


if __name__ == '__main__':
    """
    Bases functionality on if it's imported or ran directly
    """
    main()