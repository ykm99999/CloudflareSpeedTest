import base64
import json
import requests
import os

# ✅ 修改为你的目标仓库和文件路径
REPO = "ykm99999/txt"
FILE_PATH = "ip.txt"
COMMIT_MESSAGE = "自动更新优选 IP 列表"

# ✅ 从环境变量读取 GitHub Token
GH_TOKEN = os.getenv("GH_TOKEN")
if not GH_TOKEN:
    raise Exception("未设置 GH_TOKEN 环境变量")

# ✅ 获取文件内容并编码
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()
    encoded_content = base64.b64encode(content.encode()).decode()  

# ✅ 获取当前文件的 SHA（用于覆盖）
url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
headers = {
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
response = requests.get(url, headers=headers)
if response.status_code == 200:
    sha = response.json()["sha"]
else:
    sha = None  # 文件不存在则创建新文件

# ✅ 构造上传请求
payload = {
    "message": COMMIT_MESSAGE,
    "content": encoded_content,
    "branch": "main"
}
if sha:
    payload["sha"] = sha

upload_response = requests.put(url, headers=headers, data=json.dumps(payload))

if upload_response.status_code in [200, 201]:
    print("✅ 上传成功！")
else:
    print("❌ 上传失败：", upload_response.status_code)
    print(upload_response.text)
