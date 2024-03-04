import subprocess
import ipaddress

network = ["192.168.3.0","192.168.3.1", "192.168.3.2", "192.168.3.3", "192.168.3.4"]  # Replace with your network range

def ping_ip(ip):
    try:
        subprocess.check_output(["ping", "-c", "1", ip], stderr=subprocess.STDOUT, timeout=1)
        return True
    except subprocess.CalledProcessError:
        return False
    except subprocess.TimeoutExpired:
        return False

def find():
    ips = []
    for ip in network:
        print("checking ip address " +str(ip))
        if ping_ip(str(ip)):
            print(f"Found active device at {ip}")
            ips.append(ip)

    return ips
