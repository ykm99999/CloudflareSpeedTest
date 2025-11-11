import requests
import time

INPUT_FILE = "ip.txt"
OUTPUT_FILE = "ip.txt"
PORT = 16097
API_URL = "http://ip-api.com/json/{}?lang=zh-CN"

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
        country = get_country(ip)
        results.append(f"{ip}:{PORT}#{country}")
        print(f"{ip} → {country}")
        time.sleep(1.2)  # 避免 API 限速

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(results))

if __name__ == "__main__":
    process_ips()