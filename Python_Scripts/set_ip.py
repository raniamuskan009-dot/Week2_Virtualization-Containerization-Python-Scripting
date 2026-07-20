import argparse
import subprocess
import datetime

LOG_FILE = "/var/log/ip-config.log"

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def apply_ip(ip, gw, iface):
    netplan_content = f"""network:
  version: 2
  ethernets:
    {iface}:
      dhcp4: no
      addresses:
        - {ip}
      gateway4: {gw}
      nameservers:
        addresses: [8.8.8.8]
"""
    config_path = f"/etc/netplan/99-set-ip-{iface}.yaml"
    try:
        with open(config_path, "w") as f:
            f.write(netplan_content)
        subprocess.run(["sudo", "netplan", "apply"], check=True)
        log(f"Applied IP {ip} on {iface} with gateway {gw}")
    except Exception as e:
        log(f"ERROR applying IP config: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set static IP via netplan")
    parser.add_argument("--ip", required=True, help="Static IP with CIDR, e.g. 192.168.56.20/24")
    parser.add_argument("--gw", required=True, help="Gateway IP")
    parser.add_argument("--iface", required=True, help="Interface name, e.g. eth0")
    args = parser.parse_args()
    apply_ip(args.ip, args.gw, args.iface)