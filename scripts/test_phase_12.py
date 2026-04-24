import os
import sys

checks = []

def check(desc, passed):
    checks.append((desc, passed))
    print(f"{'[PASS]' if passed else '[FAIL]'} {desc}")

# Read files
with open("frontend/app.js", encoding="utf-8") as f:
    appjs = f.read()

with open("frontend/index.html", encoding="utf-8") as f:
    html = f.read()

# app.js — filter functions present
check("app.js contiene applyTradeFilters()", "applyTradeFilters" in appjs)
check("app.js contiene populateMarketFilter()", "populateMarketFilter" in appjs)
check("app.js contiene tradesCache", "tradesCache" in appjs)
check("app.js contiene filtro setup_valid", "setup_valid" in appjs)
check("app.js contiene filtro discipline_label", "discipline_label" in appjs)
check("app.js contiene filtro emotional_state", "emotional_state" in appjs)
check("app.js contiene filtro result_r", "result_r" in appjs)

# index.html — filter controls present
check("index.html contiene filter_setup", "filter_setup" in html)
check("index.html contiene filter_disciplina", "filter_disciplina" in html)
check("index.html contiene filter_emocion", "filter_emocion" in html)
check("index.html contiene filter_resultado", "filter_resultado" in html)
check("index.html contiene filter_mercado", "filter_mercado" in html)
check("index.html contiene tradesCount", "tradesCount" in html)
check("index.html contiene Mostrando", "Mostrando" not in html)  # rendered by JS, not hardcoded

# Backend files unchanged (no filter logic injected)
backend_ok = True
for root, dirs, files in os.walk("backend"):
    for fname in files:
        if not fname.endswith(".py"):
            continue
        with open(os.path.join(root, fname), encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if "applyTradeFilters" in content or "filter_setup" in content:
            backend_ok = False
check("archivos backend sin cambios de filtro", backend_ok)

print()
all_passed = all(p for _, p in checks)
print("RESULTADO FINAL:", "PASS" if all_passed else "FAIL")
sys.exit(0 if all_passed else 1)
