"""Script used to upgrade Versa CPE automatically
"""

from pexpect import pxssh
from email.mime import image
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pexpect
import sys
import re
import time
import subprocess
from datetime import datetime
import smtplib
from requests import session
global max_retry_timeout, image_version, script_is_running, completed_file, image_filename, image_date, image_id, hosts_path, sender_address, sender_pass, receiver_address
import os

###############################################
####### Variables you can change ##############
###############################################

#Image file name, KEEP ORIGIONAL NAME FORMATTING, IT'S USED IN THE SCRIPT AND TO VERIFY IMAGE. 
image_filename = "versa-flexvnf-20220420-131241-eca39c5-21.1.4-wsm.bin"

#File used to register all upgraded devices. 
completed_file = "completed_devices.txt"

#IP used for the port
hostname = "172.16.102.1"

#Path to the ssh hosts file, we need to delete it as the IP stays the same but the ssh key changes with device swap. 
hosts_path = "/home/versaupgrade/.ssh/known_hosts"

#Change to whatever E-mail you want to use to send/recieve. 
sender_address = 'exampleemail@gmail.com'
#This is not the normal login password, you'll have to get one that can be used for these services. 
sender_pass = 'examplepassword'
receiver_address = 'exampleemail@gmail.com'


###############################################
###### DONT TOUCH THESE VARIABLES #############
###############################################

prompt = "\$"
script_is_running = True
username = "admin"
password = "versa123"
max_retry_timeout = 5
image_attributes = image_filename.split("-")
image_date = image_attributes[2]
image_id = image_attributes[4]
image_version = image_attributes[5]

def versa_parse_output(command_output, matching_string):
    """
    Filter output from vsh details
    """
    variable_get = re.findall(r"[\n\r].*" + matching_string + "\s*([^\n\r\t]*)", command_output)
    return variable_get[0]


def die(child, errstr):
    """
    Kill selected pexpect instance.
    """
    print(errstr)
    print(child.before, child.after)
    child.terminate()
    
def send_and_expect(ch, send, expect):
    """
    Send and Expect with pexpect, return decoded output.
    """
    ch.sendline(send)
    ch.expect([expect, pexpect.EOF, pexpect.TIMEOUT])
    output = ch.before.decode()
    return output


def versa_get_attributes(ch):
    """
    Get the attributes required to evaluate what the next step should be.
    """
    correct_image_exists = False
    image_check = False
    vsh_running = False
    send_and_expect(ch, password, prompt)
    output_status = send_and_expect(ch, 'vsh status', 'admin:')
    send_and_expect(ch, password, prompt)
    output_ls = send_and_expect(ch, 'ls /home/versa/packages', prompt)
    output_vsh = send_and_expect(ch, 'vsh details', prompt)
    ch.terminate()

    if "Stopped" in output_status:
        vsh_running = False
    else:
        vsh_running = True

    if image_filename in output_ls:
        correct_image_exists = True
    else:
        correct_image_exists = False
    global active_sn
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


def scp_image_file_upload():
    """
    Upload image to device if it does not already exist.
    """
    try:
        cmd = f'sshpass -p {password} scp -o StrictHostKeyChecking=no {image_filename} {username}@{hostname}:/home/versa/packages/'
        output = subprocess.check_output(cmd, shell=True)
        print(output)
        return True
    except:
        return False


def send_mail():
    """
    When device is successfully upgraded, we send an E-mail showing output of some commands.
    """
    try: 
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
        ch.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
        send_and_expect(ch, password, prompt)
        send_and_expect(ch, 'vsh status', 'admin:')
        output_status = send_and_expect(ch, password, prompt)
        output_ls = send_and_expect(ch, 'ls /home/versa/packages', prompt)
        output_vsh = send_and_expect(ch, 'vsh details', prompt)

        send_and_expect(ch, 'cli', 'cli>')
        output_interfaces = send_and_expect(ch, "show interfaces brief | tab | nomore", "cli>")
        ch.terminate()

        mail_content = f'Device {active_sn} successfully upgraded.\n\
            ------------------------------------------------------------------------\n\
            --------------------------------VSH DETAILS--------------------\n\
            ------------------------------------------------------------------------\n\
            {output_vsh}\n\
            ------------------------------------------------------------------------\n\
            --------------------------------VSH STATUS---------------------\n\
            ------------------------------------------------------------------------\n\
            {output_status}\n\
            ------------------------------------------------------------------------\n\
            --------------------------------LS PACKAGES--------------------\n\
            ------------------------------------------------------------------------\n\
            {output_ls}\n\
            ------------------------------------------------------------------------\n\
            --------------------------------INTERFACES---------------------\n\
            ------------------------------------------------------------------------\n\
            {output_interfaces}\n\
            '
        #The mail addresses and password

        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = f'Device {active_sn} successfully upgraded.'   #The subject line
        #The body and the attachments for the mail
        message.attach(MIMEText(mail_content, 'plain'))
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print("Mail sent")
    except:
        print("Mail not sent")
        print("Confirm you have the correct login details")


def device_completed_steps():
    """
    Add the device to a list and send an E-mail. This is to stop infinite E-mail / informs. 
    """
    Found = False
    device_list = open(completed_file, 'r')
    read_device_list = device_list.readlines()
    device_list.close()
    for line in read_device_list:
        if active_sn in line:
            print(f"Device already exists in list, nothing is done.")
            Found = True
    if not Found:
        date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
        device_list = open(completed_file, 'a')
        device_list.write("Serial Number: " + active_sn + " | added on : " + date + "\n")
        device_list.close()
        print("Adding device and sending E-mail containing interface and vsh output")
        send_mail()


def versa_upgrade():
    """
    Runs the command required to upgrade the device.
    """
    try:
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
        ch.logfile = sys.stdout.buffer
        ch.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
        send_and_expect(ch, password, prompt)
        send_and_expect(ch, "cli", "cli>")
        send_and_expect(ch, f"request system package upgrade {image_filename}", "[no,yes]")
        output_upgrade = send_and_expect(ch, "yes", "cli>")
        return True
    except:
        return False


def versa_connect():
    """
    Connects to the device and opens a session with the device to confirm connectivity before we proceed. 
    """
    start_time = time.time()
    upgrade_required = True
    while time.time() - start_time <= max_retry_timeout:
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
        session_callback = ch.expect([pexpect.TIMEOUT, pexpect.EOF, 'yes/no', 'assword:', 'Connection refused', prompt] )
        print(f"Currently using session_callback: {session_callback}")
        if session_callback == 0:
            die(ch, 'ERROR!\nSSH timed out. Here is what SSH said:' )
            return False, False, False, False, False
        elif session_callback == 1:
            die(ch, 'ERROR!\nSSH had an EOF error, here is what it said:' )
            return False, False, False, False, False
        elif session_callback == 2:
            send_and_expect(ch, 'yes', 'assword:')
            send_and_expect(ch, password, prompt)
        elif session_callback == 3:
            try:
                versa_attributes = versa_get_attributes(ch)
                return True, versa_attributes[1], versa_attributes[2], versa_attributes[3], True
            except:
                return False, False, False, False, False

        elif session_callback == 4:
            time.sleep(0.5)
        else:
            time.sleep(0.5)
            break
    else:
        return False


def main():
    #resets the sn variable. 
    active_sn = ""
    #Reset ssh keys
    os.remove(hosts_path)
    while script_is_running is True:
        versa_variables = versa_connect()
        print(versa_variables)
        confirm_versa_status = versa_variables[3]
        confirm_versa_file = versa_variables[2]
        confirm_versa_version = versa_variables[1]
        confirm_versa_login = versa_variables[0]
        confirm_versa_vsh_access= versa_variables[4]
        print(f"\
            Versa login         : {confirm_versa_login}\n\
            Versa Version       : {confirm_versa_version}\n\
            Versa Image file    : {confirm_versa_file}\n\
            Versa statuses      : {confirm_versa_status}\n\
            Versa VSH available : {confirm_versa_vsh_access}\n\
            ")

        if confirm_versa_login is True:
            print("Login successful")
            if confirm_versa_status is True:
                print("All services are running")
                if confirm_versa_file is True:
                    print("Correct image version exists on device")
                    if confirm_versa_version is True:
                        print("Device checks completed and device successfully upgraded, waiting 5 minutes")
                        device_completed_steps()
                        time.sleep(300)
                        
                    else:
                        print("Device is not upgraded, starting the upgrade process")
                        if not versa_upgrade():
                            print('Upgrade failed')
                            print("Will wait 5 minutes and try again ")
                            time.sleep(300)
                        else:
                            print("Upgrade started, pausing everything for 10 minutes")
                            time.sleep(600)
                else:
                    print("Image does not exist on device")
                    if not scp_image_file_upload():
                        print("upload of file failed")
                        print("Will wait 5 minutes and try again ")
                        time.sleep(300)
                    else:
                        print("upload of file successful")

            else:
                print("Some services have stopped")
                print("Will wait 5 minutes and see if they have started. ")
                time.sleep(300)
        else:
            print("Login not successful")
            print("Will wait 5 minutes and see if we have connection. ")
            time.sleep(300)


if __name__ == '__main__':
    main()

