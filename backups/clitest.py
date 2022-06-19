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

from requests import session

global max_retry_timeout, image_version, script_is_running
script_is_running = True

prompt = "\$"

hostname = "172.16.102.1"
username = "admin"
password = "versa123"
max_retry_timeout = 5


ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
ch.logfile = sys.stdout
ch.sendline(password)
ch.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
ch.sendline("cli")
ch.expect(["cli>", pexpect.EOF, pexpect.TIMEOUT])
output_upgrade = ch.before.decode()
print(output_upgrade)