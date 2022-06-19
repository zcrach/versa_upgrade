import sys
import os
from datetime import datetime
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
import subprocess
from datetime import datetime
import smtplib

from requests import session
script_is_running = True

prompt = "\$"

hostname = "172.16.101.1"
username = "admin"
password = "versa123"
max_retry_timeout = 5

global completed_file, active_sn
completed_file = "completed_devices.txt"
active_sn = "JAB12321312"


def send_mail():
    ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
    ch.logfile = sys.stdout.buffer
    ch.expect(['assword:', pexpect.EOF, pexpect.TIMEOUT])
    ch.sendline(password)
    ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
    #Check vsh status
    ch.sendline('vsh status')
    ch.expect(['admin:', pexpect.EOF, pexpect.TIMEOUT])
    ch.sendline(password)
    ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
    output_status = ch.before.decode()

    ch.sendline('ls /home/versa/packages') 
    ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
    output_ls = ch.before.decode()

    #Check vsh details
    ch.sendline('vsh details') 
    ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
    output_vsh = ch.before.decode()

    ch.sendline("cli")
    ch.expect(["cli>", pexpect.EOF, pexpect.TIMEOUT])
    ch.sendline(f"show interfaces brief | tab | nomore")
    ch.expect(["cli>", pexpect.EOF, pexpect.TIMEOUT])
    output_interfaces = ch.before.decode()
    ch.sendline('exit')

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
    sender_address = 'versaupgradescript@gmail.com'
    sender_pass = 'cjkshcimrrpgobfg'
    receiver_address = 'versaupgradescript@gmail.com'
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


def device_completed_steps():
    Found = False
    device_list = open(completed_file, 'r')
    read_device_list = device_list.readlines()
    device_list.close()
    for line in read_device_list:
        if active_sn in line:
            print(f"Found it")
            Found = True
    if not Found:
        date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
        device_list = open(completed_file, 'a')
        device_list.write("Serial Number: " + active_sn + " | added on : " + date + "\n")
        device_list.close()
        send_mail()
        

device_completed_steps()

