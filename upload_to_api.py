import base64
import json
import requests
import os

REPO = "ykm99999/txt"
FILE_PATH = "ip.txt"
BRANCH = "main"
TOKEN = os.getenv("GH_TOKEN")

def read_ips():
    try:
        with open("ip.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        print("ip.txt 文件未找到")
        return ""

def get_file_sha():
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()["sha"]
    return None

def upload(content):
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/json"
    }
    sha = get_file_sha()
    data = {
        "message": "自动更新优选 IP",
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha

    r = requests.put(url, headers=headers, data=json.dumps(data))
    print("上传状态：", r.status_code)
    print("返回内容：", r.text)

if __name__ == "__main__":
    content = read_ips()
    upload(content)