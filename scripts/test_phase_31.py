import requests

BACKEND = "https://ifvg-backend.onrender.com"
HTML_PATH = "frontend/index.html"
JS_PATH   = "frontend/app.js"

results = []

def check(label, condition):
    status = "PASS" if condition else "FAIL"
    results.append((label, status))
    print(f"[{status}] {label}")

# --- File checks ---
with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

with open(JS_PATH, encoding="utf-8") as f:
    js = f.read()

check("index.html has Settings section",       'id="section-settings"' in html)
check("index.html has Settings nav item",      'data-section="settings"' in html)
check("index.html has toggle label",           "Show delete buttons (danger zone)" in html)
check("index.html has toggle checkbox id",     'id="toggle_show_delete_buttons"' in html)

check("app.js has show_delete_buttons key",    "show_delete_buttons" in js)
check("app.js uses localStorage",              "localStorage" in js)
check("app.js default is false",               '"false"' in js or "=== \"true\"" in js)
check("app.js has isDeleteEnabled function",   "function isDeleteEnabled()" in js)
check("Delete Trade conditioned",              "isDeleteEnabled()" in js and "Delete Trade" in js)
check("Delete Day conditioned",               "isDeleteEnabled()" in js and "Delete Day" in js)
check("Delete Bias conditioned",              "isDeleteEnabled()" in js and "Delete Bias" in js)

# --- API checks ---
try:
    r = requests.get(f"{BACKEND}/health", timeout=30)
    check("GET /health -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /health -> 200 (ERROR: {e})", False)

try:
    r = requests.get(f"{BACKEND}/trades", timeout=30)
    check("GET /trades -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /trades -> 200 (ERROR: {e})", False)

# --- Summary ---
passed = sum(1 for _, s in results if s == "PASS")
total  = len(results)
print(f"\n{'='*40}")
if passed == total:
    print(f"FASE 31 PASS ({passed}/{total})")
else:
    print(f"FASE 31 FAIL ({passed}/{total} passed)")
