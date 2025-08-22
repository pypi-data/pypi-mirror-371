import os
import socket
import subprocess
import random
import string

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_external_ip():
    try:
        output = subprocess.check_output(
            "ip -o -4 addr list | grep -v '127.0.0.1'",
            shell=True, stderr=subprocess.DEVNULL
        ).decode().strip()
        for line in output.splitlines():
            ip = line.split()[3].split('/')[0]
            if ip:
                return ip
    except Exception:
        pass
    try:
        output = subprocess.check_output("hostname -I", shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if output:
            return output.split()[0]
    except Exception:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        pass
    return None

def generate_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_username(length=8):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def save_log(log_file, text):
    with open(log_file, "a") as f:
        f.write(text + "\n")
