import socket
import requests
import time

INPUT_FILE = "ip.txt"
OUTPUT_FILE = "ip.txt"
API_URL = "http://ip-api.com/json/{}?lang=zh-CN"
PORTS_TO_CHECK = [443, 80, 8080]

def detect_port(ip):
    for port in PORTS_TO_CHECK:
        try:
            with socket.create_connection((ip, port), timeout=2):
                return port
        except:
            continue
    return None

def get_country(ip):
    try:
        r = requests.get(API_URL.format(ip), timeout=5)
        data = r.json()
        if data["status"] == "success":
            return data["country"]
    except:
        pass
    return "未知"

def process_ips():
    try:
        with open(INPUT_FILE, "r") as f:
            ips = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("未找到 ip.txt")
        return

    results = []
    for ip in ips:
        port = detect_port(ip)
        country = get_country(ip)
        if port:
            results.append(f"{ip}:{port}#{country}")
            print(f"{ip}:{port} → {country}")
        else:
            print(f"{ip} 无开放端口，跳过")
        time.sleep(1.2)

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    process_ips()
