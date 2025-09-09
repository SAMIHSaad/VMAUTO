
import os
import time

IP_FILE = "ips.txt"
LOCK_FILE = "ips.lock"
IP_RANGE_START = 100
IP_RANGE_END = 200
IP_PREFIX = "192.168.122"

def acquire_lock():
    while os.path.exists(LOCK_FILE):
        time.sleep(0.1)
    open(LOCK_FILE, "w").close()

def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def initialize_ip_pool():
    if not os.path.exists(IP_FILE):
        with open(IP_FILE, "w") as f:
            for i in range(IP_RANGE_START, IP_RANGE_END + 1):
                f.write(f"{IP_PREFIX}.{i}\n")

def get_available_ip():
    acquire_lock()
    try:
        with open(IP_FILE, "r+") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                line = line.strip()
                if not line.endswith(" # used"):
                    ip = line
                    lines[i] = f"{line} # used\n"
                    f.seek(0)
                    f.writelines(lines)
                    return ip
    finally:
        release_lock()
    return None

def release_ip(ip_to_release):
    acquire_lock()
    try:
        with open(IP_FILE, "r+") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.strip() == f"{ip_to_release} # used":
                    lines[i] = f"{ip_to_release}\n"
                    f.seek(0)
                    f.writelines(lines)
                    f.truncate()
                    break
    finally:
        release_lock()

if __name__ == "__main__":
    initialize_ip_pool()
    ip = get_available_ip()
    if ip:
        print(ip)
