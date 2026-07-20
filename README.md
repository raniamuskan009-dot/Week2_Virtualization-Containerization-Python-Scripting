# Week 2 — Virtualization, Containerization & Python Scripting

**Author:** Rania Muskan Malik
**Internship:** Snskies Private Limited
**Subject Area:** Network Automation & Infrastructure Lab

## Overview

This project builds a mini private network lab using two VMs connected on
a VirtualBox host-only network, each running a Docker container, with
Python scripts to automate IP configuration and health monitoring.

## Project Structure

```
Week2_Submission/
├─ Week2_Lab_Report.pdf       
│                              
├─ Diagrams/
│  └─ network_topology.png    
├─ Screenshots/                
├─ Python_Scripts/
│  ├─ set_ip.py                
│  └─ monitor.py                
├─ Docker_Configs/
│  ├─ infra-server-compose.yml 
│  └─ admin-tools-compose.yml 
├─ Output_Logs/
│  ├─ ip-config.log           
│  └─ healthcheck.log         
└─ README.md
```

## Setup

Two VMs on a VirtualBox **host-only network** (`192.168.56.0/24`):

| VM | OS | IP | Role |
|---|---|---|---|
| infra-server | Ubuntu Server 22.04 | 192.168.56.10 | Runs Nginx container |
| admin-tools | Kali Linux | 192.168.56.20 | Runs Syslog-NG container |

Both VMs also have a **second (NAT) adapter**, since host-only networking
alone has no internet access and Docker needs to reach the internet to
pull images.

## How to Run

### 1. Build the containers

On **infra-server**:
```bash
docker network create web-net
docker run -d --name web --network web-net -p 8080:80 nginx
```

On **admin-tools**:
```bash
docker network create log-net
docker run -d --name logger --network log-net -p 514:514/udp balabit/syslog-ng
```

### 2. Set a static IP (set_ip.py)

Run on either VM:
```bash
sudo python3 set_ip.py --ip <ip/cidr> --gw <gateway> --iface <interface>
```
Example:
```bash
sudo python3 set_ip.py --ip 192.168.56.20/24 --gw 192.168.56.1 --iface eth0
```
Logs to `/var/log/ip-config.log`.

### 3. Run health checks (monitor.py)

Run on **admin-tools** (infra-server must be up and running its container):
```bash
pip3 install requests --break-system-packages
python3 monitor.py
```
Logs to `healthcheck.log` in the working directory.

## Known Issue

`set_ip.py` writes a `gateway4` route into netplan. Since the lab's gateway
(`192.168.56.1`) is a dummy address, applying it can override the real
internet-facing default route provided by the NAT adapter. If internet
access breaks after running the script, clear the conflicting route:
```bash
sudo ip route del default via 192.168.56.1 dev <iface>
```

## Bonus — Packet Analysis

Wireshark/tcpdump captures are included in `Screenshots/` covering:
- HTTP traffic (admin-tools → Nginx) with header analysis
- ICMP echo between VMs with TTL values
- Syslog UDP 514 traffic (infra-server → Syslog-NG) with payload
- A tcpdump `.pcap` capture opened in Wireshark

See `Week2_Lab_Report.pdf` for full write-ups, the security note on
plaintext HTTP vs HTTPS, and the reflection section.
