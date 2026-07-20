import subprocess
import requests
import datetime
import time

LOG_FILE = "healthcheck.log"
TARGET_IP = "192.168.56.10"
NGINX_URL = f"http://{TARGET_IP}:8080"

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    print(line)

def check_ping():
    result = subprocess.run(
        ["ping", "-c", "2", TARGET_IP],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.returncode == 0

def check_http():
    try:
        response = requests.get(NGINX_URL, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_syslog():
    test_message = f"Health test {datetime.datetime.now()}"
    subprocess.run(["logger", test_message])
    time.sleep(1)
    result = subprocess.run(
        ["sudo", "docker", "logs", "logger"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    return result.returncode == 0

def run_health_check():
    ping_ok = check_ping()
    http_ok = check_http()
    syslog_ok = check_syslog()

    status_line = (
        f"PING {TARGET_IP} {'OK' if ping_ok else 'FAIL'} | "
        f"HTTP {'200 OK' if http_ok else 'FAIL'} | "
        f"SYSLOG {'RECEIVED' if syslog_ok else 'FAIL'}"
    )
    log(status_line)

    if not (ping_ok and http_ok and syslog_ok):
        log("ALERT: One or more checks failed!")

if __name__ == "__main__":
    run_health_check()