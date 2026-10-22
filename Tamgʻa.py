import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import base64
import json
import time
import sys

# ==========================================
# SOZLAMALAR (O'zingizga moslang!)
# ==========================================
GITHUB_TOKEN = "YOUR_TOKEN" # ghp_... bilan boshlanadi
REPO_OWNER = "Dasturchi-top-1"  # GitHub username yoki tashkilot nomi
REPO_NAME = "Dasturchi-top-1"   # Loyiha (repo) nomi
BRANCH = "main"                 # Asosiy shoxobcha (main yoki master)

MARKER = "Ishlab chiqaruvchi: Blip"
COMMIT_MESSAGE = "Avtomatik qo'shildi: Ishlab chiqaruvchi Blip tamg'asi"

# Qo'llab-quvvatlanadigan fayl turlari va ularning izoh belgilari
COMMENTS = {
    ".py": "#", ".sh": "#", ".rb": "#", ".yml": "#", ".yaml": "#", 
    ".toml": "#", ".ini": "#", ".conf": "#", ".env": "#", 
    ".js": "//", ".jsx": "//", ".ts": "//", ".tsx": "//", ".java": "//", 
    ".c": "//", ".cpp": "//", ".cs": "//", ".go": "//", ".rs": "//", 
    ".css": "/*", ".scss": "/*", ".html": "<!--", ".htm": "<!--", ".xml": "<!--"
}

# ==========================================
# TARMOQ SOZLAMALARI (RETRY)
# ==========================================
# Agar tarmoq uzilsa yoki GitHub xato bersa, 5 marta qayta urinadi
retry_strategy = Retry(
    total=5, 
    backoff_factor=2, 
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "PUT"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)

# ==========================================
# YORDAMCHI FUNKSIYALAR
# ==========================================
def make_stamp(extension):
    comment = COMMENTS.get(extension)
    if not comment: return None
    if comment == "<!--": return f"<!-- {MARKER} -->"
    if comment == "/*": return f"/* {MARKER} */"
    return f"{comment} {MARKER}"

def get_file_content_and_sha(filepath):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filepath}?ref={BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        res = session.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            return content, data['sha']
    except requests.exceptions.RequestException:
        pass
    return None, None

def update_file(filepath, new_content, sha):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{filepath}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    encoded_content = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
    payload = {
        "message": COMMIT_MESSAGE,
        "content": encoded_content,
        "sha": sha,
        "branch": BRANCH
    }
    try:
        res = session.put(url, headers=headers, data=json.dumps(payload), timeout=15)
        return res.status_code in [200, 201]
    except requests.exceptions.RequestException:
        return False

# ==========================================
# ASOSIY MANTIQ
# ==========================================
def process_repository():
    print(f"🚀 GitHub bilan ulanish: {REPO_OWNER}/{REPO_NAME}...")
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    tree_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/git/trees/{BRANCH}?recursive=1"
    try:
        res = session.get(tree_url, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"❌ Xato: Repozitoriyni o'qib bo'lmadi. Status: {res.status_code}")
            print("Tokenni, repo nomini yoki 'main' tarmog'ini to'g'riligini tekshiring.")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Tarmoq xatosi: {e}")
        return

    # Faqat ruxsat etilgan kengaytmali fayllarni ajratib olamiz
    files = []
    for f in res.json().get("tree", []):
        if f["type"] == "blob" and "." in f["path"]:
            ext = "." + f["path"].split(".")[-1]
            if ext in COMMENTS:
                files.append(f)

    total_files = len(files)
    print(f"📂 Jami tekshiriladigan kod fayllari: {total_files} ta\n")
    
    count_added = 0
    count_skipped = 0
    count_error = 0

    for index, file in enumerate(files, start=1):
        filepath = file["path"]
        ext = "." + filepath.split(".")[-1]
        
        # Har bir faylda [1/50] kabi ko'rsatkich chiqaradi
        print(f"[{index}/{total_files}] 🔍 {filepath}...", end=" ", flush=True)
        
        content, sha = get_file_content_and_sha(filepath)
        
        if content is None: 
            print("❌ O'qib bo'lmadi")
            count_error += 1
            continue

        if MARKER in content:
            print("⏩ O'tkazib yuborildi")
            count_skipped += 1
            continue

        stamp = make_stamp(ext)
        if not stamp: continue

        # Fayl oxiriga qo'shish mantiqi
        if not content.endswith("\n"):
            new_content = content + "\n\n" + stamp + "\n"
        else:
            new_content = content + "\n" + stamp + "\n"

        if update_file(filepath, new_content, sha):
            print("✅ Qo'shildi")
            count_added += 1
        else:
            print("❌ Xato yuz berdi")
            count_error += 1
        
        # Kutish vaqti 0.5 soniya qilib belgilandi (limitga tushmaslik uchun)
        time.sleep(0.5)

    print("\n" + "="*45)
    print(f"🎉 Tugadi!")
    print(f"✅ Qo'shildi: {count_added}")
    print(f"⏩ O'tkazib yuborildi: {count_skipped}")
    print(f"❌ Xato: {count_error}")
    print("="*45)

if __name__ == "__main__":
    process_repository()