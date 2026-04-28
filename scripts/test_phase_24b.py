import requests

BASE = "http://localhost:5000"
CSS_PATH = "frontend/styles.css"

def check(label, ok):
    print(f"{'PASS' if ok else 'FAIL'} - {label}")
    return ok

results = []

# CSS class checks
with open(CSS_PATH, "r") as f:
    css = f.read()

results.append(check("styles.css has .confirm-grid",  ".confirm-grid" in css))
results.append(check("styles.css has .confirm-item",  ".confirm-item" in css))
results.append(check("styles.css has .btn-primary",   ".btn-primary" in css))
results.append(check("styles.css has input:focus",    ":focus" in css))

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
total = len(results)
print(f"{'FASE 24B PASS' if passed == total else 'FASE 24B FAIL'} ({passed}/{total})")
