import requests
import os

BASE = "http://127.0.0.1:8000"
FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend")

def check(label, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}" + (f" — {detail}" if detail else ""))
    return ok

def read_file(name):
    with open(os.path.join(FRONTEND, name), encoding="utf-8") as f:
        return f.read()

results = []

# 1. GET /health
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    results.append(check("GET /health -> 200", r.status_code == 200))
except Exception as e:
    results.append(check("GET /health -> 200", False, str(e)))

# 2. GET /trades
try:
    r = requests.get(f"{BASE}/trades", timeout=5)
    results.append(check("GET /trades -> 200", r.status_code == 200))
except Exception as e:
    results.append(check("GET /trades -> 200", False, str(e)))

# 3. GET /metrics
try:
    r = requests.get(f"{BASE}/metrics", timeout=5)
    results.append(check("GET /metrics -> 200", r.status_code == 200))
except Exception as e:
    results.append(check("GET /metrics -> 200", False, str(e)))

# Read frontend files
html = read_file("index.html")
js   = read_file("app.js")

# 4. index.html contiene navegación
results.append(check(
    "index.html contiene navegación",
    "nav-menu" in html and "nav-item" in html
))

# 5. index.html contiene las 6 secciones
sections = {
    "Dashboard":    "section-dashboard" in html,
    "Trading Day":  "section-trading-day" in html,
    "Nuevo Trade":  "section-nuevo-trade" in html,
    "Journal":      "section-journal" in html,
    "Reportes":     "section-reportes" in html,
    "Estrategia":   "section-estrategia" in html,
}
for name, present in sections.items():
    results.append(check(f"index.html contiene sección: {name}", present))

# 6. app.js contiene función para cambiar secciones
results.append(check(
    "app.js contiene función showSection",
    "function showSection" in js
))

# 7. Dashboard sigue usando métricas
results.append(check(
    "Dashboard usa métricas (metricsSummary + loadMetrics)",
    "metricsSummary" in html and "loadMetrics" in js
))

# 8. Journal sigue usando filtros
results.append(check(
    "Journal usa filtros (applyTradeFilters + trade_search)",
    "applyTradeFilters" in js and 'id="trade_search"' in html
))

# 9. Reportes sigue usando downloadMonthlyPDF
results.append(check(
    "Reportes usa downloadMonthlyPDF",
    "downloadMonthlyPDF" in js and "downloadMonthlyPDF" in html
))

# 10. IDs existentes no eliminados
ids_required = ["trading_day_form", "trade_form", "trade_search", "pdf_year", "pdf_month"]
for id_name in ids_required:
    results.append(check(
        f'ID preservado: {id_name}',
        f'id="{id_name}"' in html
    ))

# Summary
passed = sum(results)
total  = len(results)
print(f"\n{'='*40}")
print(f"FASE 21: {passed}/{total} checks pasaron")
if passed == total:
    print("FASE 21 PASS")
else:
    print("FASE 21 FAIL")
