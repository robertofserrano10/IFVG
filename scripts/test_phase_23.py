import requests

BASE = "http://127.0.0.1:8000"
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

results = []

def check(name, ok):
    tag = PASS if ok else FAIL
    print(f"[{tag}] {name}")
    results.append(ok)

# 1. GET /health -> 200
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    check("GET /health -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /health -> 200 ({e})", False)

# Read frontend files
try:
    with open("frontend/index.html", encoding="utf-8") as f:
        html = f.read()
except Exception as e:
    html = ""
    print(f"[WARN] Cannot read index.html: {e}")

try:
    with open("frontend/app.js", encoding="utf-8") as f:
        js = f.read()
except Exception as e:
    js = ""
    print(f"[WARN] Cannot read app.js: {e}")

try:
    with open("frontend/styles.css", encoding="utf-8") as f:
        css = f.read()
except Exception as e:
    css = ""
    print(f"[WARN] Cannot read styles.css: {e}")

# 2. index.html contains checkbox include_pdf_images
check("index.html contiene checkbox include_pdf_images", 'id="include_pdf_images"' in html)

# 3. app.js usa include_images en downloadMonthlyPDF
check("app.js usa include_images en downloadMonthlyPDF", "include_images" in js)

# 4. IDs críticos presentes
for id_name in ["trading_day_form", "trade_form", "trade_search", "pdf_year", "pdf_month"]:
    check(f"index.html conserva id={id_name}", f'id="{id_name}"' in html)

# 5. Títulos de secciones
for title in ["Dashboard", "Trading Day", "Nuevo Trade", "Journal", "Reportes", "Estrategia"]:
    check(f"index.html contiene sección '{title}'", title in html)

# 6. Clases visuales nuevas en styles.css
for cls in ["section-header", "active-nav", "strategy-card", "report-card", "responsive"]:
    check(f"styles.css contiene clase '{cls}'", cls in css)

# 7. GET /trades -> 200
try:
    r = requests.get(f"{BASE}/trades", timeout=5)
    check("GET /trades -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /trades -> 200 ({e})", False)

# 8. GET /metrics -> 200
try:
    r = requests.get(f"{BASE}/metrics", timeout=5)
    check("GET /metrics -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /metrics -> 200 ({e})", False)

total = len(results)
passed = sum(results)
print(f"\n{'='*40}")
print(f"FASE 23: {passed}/{total} checks passed")
if passed == total:
    print("RESULTADO: FASE 23 PASS")
else:
    print("RESULTADO: FASE 23 FAIL")
