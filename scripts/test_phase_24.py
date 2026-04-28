import requests

BASE = "http://127.0.0.1:8000"
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

results = []

def check(name, ok):
    tag = PASS if ok else FAIL
    print(f"[{tag}] {name}")
    results.append(ok)

try:
    with open("frontend/styles.css", encoding="utf-8") as f:
        css = f.read()
except Exception as e:
    css = ""
    print(f"[WARN] Cannot read styles.css: {e}")

try:
    with open("frontend/index.html", encoding="utf-8") as f:
        html = f.read()
except Exception as e:
    html = ""
    print(f"[WARN] Cannot read index.html: {e}")

# 1. Nueva paleta en styles.css
for color in ["#0B0F17", "#111827", "#1F2937", "#E5E7EB", "#9CA3AF",
              "#3B82F6", "#22D3EE", "#22C55E", "#EF4444", "#F59E0B"]:
    check(f"styles.css contiene color {color}", color.lower() in css.lower())

# 2. CSS variables declaradas
check("styles.css usa CSS variables (:root)", ":root" in css)
check("styles.css tiene --bg variable", "--bg:" in css)
check("styles.css tiene --blue variable", "--blue:" in css)

# 3. Clases de color utility
for cls in ["success", "error", "warning"]:
    check(f"styles.css contiene clase .{cls}", f".{cls}" in css or f"\n{cls} " in css)

# 4. Clases visuales heredadas de fase 23
for cls in ["section-header", "active-nav", "strategy-card", "report-card", "responsive"]:
    check(f"styles.css conserva clase '{cls}'", cls in css)

# 5. index.html estructura intacta (IDs críticos)
for id_name in ["trading_day_form", "trade_form", "trade_search", "pdf_year", "pdf_month", "include_pdf_images"]:
    check(f"index.html conserva id={id_name}", f'id="{id_name}"' in html)

# 6. Títulos de secciones intactos
for title in ["Dashboard", "Trading Day", "Nuevo Trade", "Journal", "Reportes", "Estrategia"]:
    check(f"index.html contiene sección '{title}'", title in html)

# 7. Card hover effect en CSS
check("styles.css tiene card hover", ".card:hover" in css)

# 8. Metric-value con font grande (1.6rem o mayor)
check("metric-value font grande (1.6rem)", "1.6rem" in css or "1.7rem" in css or "1.8rem" in css)

# 9. GET /health -> 200
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    check("GET /health -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /health -> 200 ({e})", False)

# 10. GET /metrics -> 200
try:
    r = requests.get(f"{BASE}/metrics", timeout=5)
    check("GET /metrics -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /metrics -> 200 ({e})", False)

total = len(results)
passed = sum(results)
print(f"\n{'='*40}")
print(f"FASE 24: {passed}/{total} checks passed")
if passed == total:
    print("RESULTADO: FASE 24 PASS")
else:
    print("RESULTADO: FASE 24 FAIL")
