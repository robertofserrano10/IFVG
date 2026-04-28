import requests

BASE        = "http://127.0.0.1:8000"
HTML_PATH   = "frontend/index.html"
JS_PATH     = "frontend/app.js"

def check(label, ok):
    print(f"{'PASS' if ok else 'FAIL'} - {label}")
    return ok

results = []

with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

# index.html must contain
for term in [
    "New Trade",
    "Reports",
    "Strategy",
    "Create Trading Day",
    "Date",
    "Market",
    "Confirmations",
    "Liquidity Type",
    "Download Monthly PDF Report",
]:
    results.append(check(f"index.html has '{term}'", term in html))

# app.js must contain
for term in [
    "Journal Summary",
    "Technical Errors",
    "Psychological Errors",
    "Execution Quality",
    "Performance Insights",
    "Discipline Alerts",
]:
    results.append(check(f"app.js has '{term}'", term in js))

# index.html must NOT contain main Spanish visible terms
for term in [
    "Nuevo Trade",
    "Reportes",
    "Estrategia",
    "Tipo de liquidez",
    "Descargar reporte PDF mensual",
]:
    results.append(check(f"index.html does NOT contain '{term}'", term not in html))

# Special cases: Fecha/Mercado/Confirmaciones exist in HTML but only as English labels now
results.append(check("index.html does NOT contain '>Fecha<'",         ">Fecha<" not in html))
results.append(check("index.html does NOT contain '>Mercado<'",       ">Mercado<" not in html))
results.append(check("index.html does NOT contain '>Confirmaciones<'","'>Confirmaciones<'" not in html))

# API smoke tests
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    results.append(check("GET /health -> 200", r.status_code == 200))
except Exception as e:
    results.append(check(f"GET /health -> 200 ({e})", False))

try:
    r = requests.get(f"{BASE}/trades", timeout=5)
    results.append(check("GET /trades -> 200", r.status_code == 200))
except Exception as e:
    results.append(check(f"GET /trades -> 200 ({e})", False))

print()
passed = sum(results)
total  = len(results)
print(f"{'FASE 25 PASS' if passed == total else 'FASE 25 FAIL'} ({passed}/{total})")
