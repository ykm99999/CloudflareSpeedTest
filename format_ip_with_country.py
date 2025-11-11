import ipaddress
import socket
import requests
import time
import concurrent.futures

INPUT_FILE = "ip.txt"
OUTPUT_FILE = "ip.txt"
PORTS_TO_CHECK = [443, 2053, 8443, 2096, 2083, 80]
TARGET_COUNTRIES = ["香港", "台湾", "韩国", "日本"]
API_URL = "http://ip-api.com/json/{}?lang=zh-CN"
MAX_IPS_PER_CIDR = 100  # 每个网段最多探测多少个 IP
MAX_THREADS = 20

def expand_ip(line):
    line = line.strip()
    if "/" in line:
        try:
            net = ipaddress.ip_network(line, strict=False)
            return [str(ip) for ip in list(net.hosts())[:MAX_IPS_PER_CIDR]]
        except:
            return []
    else:
        return [line]

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

def process_ip(ip):
    port = detect_port(ip)
    if not port:
        return None
    country = get_country(ip)
    if country not in TARGET_COUNTRIES:
        return None
    return f"{ip}:{port}#{country}"

def main():
    try:
        with open(INPUT_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("未找到 ip.txt")
        return

    all_ips = []
    for line in lines:
        all_ips.extend(expand_ip(line))

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(process_ip, ip): ip for ip in all_ips}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                print(result)

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    main()
