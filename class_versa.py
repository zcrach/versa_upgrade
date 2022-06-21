import logging
import pexpect
import time
import re

image_filename = "versa-flexvnf-20220420-131241-eca39c5-21.1.4-wsm.bin"
hostname = "172.16.102.1"
username = "admin"
password = "versa123"
hosts_path = "/home/versaupgrade/.ssh/known_hosts"


prompt = "\$"




class Versa:
    def __init__(self, serial_number, model, image_release):
        self.serial_number = serial_number
        self.model = model
        self.image_release = image_release
    
    def register_data(self):
        output_test = VersaConnect.send_and_expect(self, ch, "vsh details", prompt)
        print(VersaAttributes.versa_parse_output(self, output_test, "Serial number"))



class VersaAttributes:
    def __init__(self, ch):
        self.ch = ch
        
    def versa_parse_output(self, command_output, matching_string):
        variable_get = re.findall(r"[\n\r].*" + matching_string + "\s*([^\n\r\t]*)", command_output)
        return variable_get[0]


class VersaConnect:
    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password

    def send_and_expect(self, ch, send, expect):
        ch.sendline(send)
        ch.expect([expect, pexpect.EOF, pexpect.TIMEOUT])
        output = ch.before.decode()
        return output

    def login(self):
        ch = pexpect.spawn(f'ssh {username}@{hostname}', timeout=30, maxread=65535)
        session_callback = ch.expect([pexpect.TIMEOUT, pexpect.EOF, 'yes/no', 'assword:', 'Connection refused', prompt] )
        
        if session_callback == 0:
            die(ch, 'ERROR!\nSSH timed out. Here is what SSH said:' )
            return False
        elif session_callback == 1:
            die(ch, 'ERROR!\nSSH had an EOF error, here is what it said:' )
            return False
        elif session_callback == 2:
            VersaConnect.send_and_expect(self, ch, 'yes', 'assword:')
            VersaConnect.send_and_expect(self, ch, password, prompt)
        elif session_callback == 3:
            VersaConnect.send_and_expect(self, ch, password, prompt)
        elif session_callback == 4:
            time.sleep(0.5)
        else:
            time.sleep(0.5)

    def die(self, child, errstr):
        logging.error(errstr)
        logging.info(child.before)
        logging.info(child.after)
        child.terminate()


versa_login = VersaConnect(hostname, username, password)

def main():

    #Logging
    level = logging.DEBUG
    fmt = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(level=level, format=fmt)
    versa_login.login()

if __name__ == '__main__':
    main()

