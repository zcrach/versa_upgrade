
def versa_connect():
    """
    Log in to the Versa CPE and keep a consistent connection, to return time between commands.
    """
    return

def versa_hw_check():
    """
    Checks the Serial number of the device and registers it as a variable.
    Done by running vsh details from shell and filtering the output
    """
    return

def versa_vsh_check():
    """
    Checks if all statuses are running.
    Done by running vsh status, taking output and iterating through, comparing that each line has a status of "running".
    If not, the script is asked to wait for x minutes.
    """
    return



def versa_version_control():
    """
    Checks the current image version on the device.
    Done by running vsh details from shell and filtering the output
    """
    return

def versa_image_control():
    """
    Checks if the current image is the correct version or not, if not run a function.
    Done by running ls /home/versa/packages from shell and filtering the output
    If image version != correct version, run versa_image_upload()
    """
    return

def versa_version_upgrade():
    """
    If:
    versa_vsh_check is OK
    versa_hw_check is OK
    versa_version_control is OK
    versa_image_control is OK
    then:
    run request system upgrade firmware from cli
    """
    return



def versa_image_upload():
    """
    Uploads the correct image version to the device using tftp
    """
    return

def versa_send_email():
    """
    Use snmplib to send an E-mail if the process is successful.
    Include time of completion.
    The E-mail should include:
    vsh  status
    vsh details
    cli> show interfaces brief | tab | nomore
    
    vsh status and vsh details output. 
    Store as variable connected to the serial number 
    """

    return

def versa_shutdown():
    """
    If all checks are done including E-mail sent attached to the HW serial number.
    If yes, shutdown the device.
    """
    return


def main():
    """
    Run the entire script
    """
    return


if __name__ == '__main__':
    """
    Bases functionality on if it's imported or ran directly
    """
    main()