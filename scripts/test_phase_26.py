import os
import subprocess
import requests

BASE = "http://127.0.0.1:8000"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

results = []

def check(name, passed):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    results.append(passed)

# 1. GET /health -> 200
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    check("GET /health -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /health -> 200 ({e})", False)

# 2. .env not tracked by git
try:
    result = subprocess.run(
        ["git", "ls-files", "backend/.env"],
        cwd=ROOT, capture_output=True, text=True
    )
    check(".env not tracked by git", result.stdout.strip() == "")
except Exception as e:
    check(f".env not tracked by git ({e})", False)

# 3. backend/requirements.txt exists
req_path = os.path.join(ROOT, "backend", "requirements.txt")
check("backend/requirements.txt exists", os.path.isfile(req_path))

# 4. docs/DEPLOY.md exists
deploy_path = os.path.join(ROOT, "docs", "DEPLOY.md")
check("docs/DEPLOY.md exists", os.path.isfile(deploy_path))

# 5. docs/DEPLOY.md mentions Render
if os.path.isfile(deploy_path):
    content = open(deploy_path, encoding="utf-8").read()
    check("docs/DEPLOY.md mentions Render", "Render" in content)
else:
    check("docs/DEPLOY.md mentions Render", False)

# 6. docs/DEPLOY.md mentions SUPABASE_SERVICE_ROLE_KEY
if os.path.isfile(deploy_path):
    content = open(deploy_path, encoding="utf-8").read()
    check("docs/DEPLOY.md mentions SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_ROLE_KEY" in content)
else:
    check("docs/DEPLOY.md mentions SUPABASE_SERVICE_ROLE_KEY", False)

# 7. frontend/config.js exists
config_js = os.path.join(ROOT, "frontend", "config.js")
check("frontend/config.js exists", os.path.isfile(config_js))

# 8. index.html loads config.js before app.js
index_html = os.path.join(ROOT, "frontend", "index.html")
if os.path.isfile(index_html):
    html = open(index_html, encoding="utf-8", errors="ignore").read()
    pos_config = html.find("config.js")
    pos_app = html.find("app.js")
    check("index.html loads config.js before app.js", pos_config != -1 and pos_app != -1 and pos_config < pos_app)
else:
    check("index.html loads config.js before app.js", False)

# 9. frontend/app.js uses configurable BACKEND_URL
app_js = os.path.join(ROOT, "frontend", "app.js")
if os.path.isfile(app_js):
    js = open(app_js, encoding="utf-8", errors="ignore").read()
    check("frontend/app.js uses configurable BACKEND_URL", "APP_CONFIG" in js and "BACKEND_URL" in js)
else:
    check("frontend/app.js uses configurable BACKEND_URL", False)

# 10. No service role key in frontend files
frontend_dir = os.path.join(ROOT, "frontend")
found_key = False
for fname in os.listdir(frontend_dir):
    fpath = os.path.join(frontend_dir, fname)
    if os.path.isfile(fpath):
        if "service_role" in open(fpath, encoding="utf-8", errors="ignore").read().lower():
            found_key = True
check("No service role key in frontend", not found_key)

print()
passed = sum(results)
total = len(results)
print(f"{'FASE 26 PASS' if all(results) else 'FASE 26 FAIL'} — {passed}/{total} checks passed")
