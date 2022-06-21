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
    def __init__(self, serial_number, release, package_id, release_date, package_folder):
        self.serial_number = serial_number
        self.release = release
        self.package_id = package_id
        self.release_date = release_date
        self.package_folder = package_folder


class VersaAttributes:
    def __init__(self, ch):
        self.ch = ch


    def versa_parse_output(self, ch, command, matching_string):
        output = VersaConnect.send_and_expect(self, ch, command, prompt)
        variable_get = re.findall(r"[\n\r].*" + matching_string + "\s*([^\n\r\t]*)", output)
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

    def cli_send_and_expect(self, ch, send):
        ch.sendline("cli")
        ch.expect(["cli>", pexpect.EOF, pexpect.TIMEOUT])
        ch.sendline(send)
        ch.expect(["cli>", pexpect.EOF, pexpect.TIMEOUT])
        output = ch.before.decode()
        ch.sendline("exit")
        ch.expect(["\$", pexpect.EOF, pexpect.TIMEOUT])
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
            VersaConnect.login.serial_number = VersaAttributes.versa_parse_output(self, ch, "vsh details", "Serial number")
            VersaConnect.login.release = VersaAttributes.versa_parse_output(self, ch, "vsh details", "Release")
            VersaConnect.login.package_id = VersaAttributes.versa_parse_output(self, ch, "vsh details", "Package id")
            VersaConnect.login.release_date = VersaAttributes.versa_parse_output(self, ch, "vsh details", "Release date")
            VersaConnect.login.package_folder = VersaConnect.send_and_expect(self, ch, 'ls /home/versa/packages', prompt)
            VersaConnect.send_and_expect(self, ch, 'vsh status', "admin:")
            VersaConnect.login.vsh_status = VersaConnect.send_and_expect(self, ch, password, prompt)
            VersaConnect.login.show_interfaces = VersaConnect.cli_send_and_expect(self, ch, 'show interfaces brief | tab | nomore')
        elif session_callback == 4:
            time.sleep(0.5)
        else:
            time.sleep(0.5)


    def die(self, child, errstr):
        logging.error(errstr)
        logging.info(child.before)
        logging.info(child.after)
        child.terminate()


def main():
    #Logging
    level = logging.DEBUG
    fmt = '[%(levelname)s] %(asctime)s - %(message)s'
    logging.basicConfig(level=level, format=fmt)
    #Versa creation
    versa_login = VersaConnect(hostname, username, password)
    versa_login.login()
    Versa_CPE = Versa(versa_login.login.serial_number, versa_login.login.release, versa_login.login.package_id, versa_login.login.release_date, versa_login.login.package_folder, versa_login.login.vsh_status, versa_login.login.show_interfaces)

    print(Versa_CPE.show_interfaces)

    if Versa_CPE.release and Versa_CPE.package_id and Versa_CPE.release_date in image_filename:
        logging.info(f"Device has the correct Version {Versa_CPE.release}")
    else:
        print("didnt work")
    #print(Versa_CPE.serial_number)
    #print(Versa_CPE.release)
    #print(Versa_CPE.package_id)
    #print(Versa_CPE.release_date)
    #print(Versa_CPE.package_folder)
if __name__ == '__main__':
    main()

