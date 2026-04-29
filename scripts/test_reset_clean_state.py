import requests

BASE = "http://127.0.0.1:8000"

results = []

def check(name, passed):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}")
    results.append(passed)

# 1. GET /trading-days -> 200 and []
try:
    r = requests.get(f"{BASE}/trading-days", timeout=5)
    data = r.json()
    check("GET /trading-days -> 200", r.status_code == 200)
    check("GET /trading-days -> []", isinstance(data, list) and len(data) == 0)
except Exception as e:
    check(f"GET /trading-days ({e})", False)
    check("GET /trading-days -> []", False)

# 2. GET /trades -> 200 and []
try:
    r = requests.get(f"{BASE}/trades", timeout=5)
    data = r.json()
    check("GET /trades -> 200", r.status_code == 200)
    check("GET /trades -> []", isinstance(data, list) and len(data) == 0)
except Exception as e:
    check(f"GET /trades ({e})", False)
    check("GET /trades -> []", False)

# 3. GET /trade-images -> 200 and []
try:
    r = requests.get(f"{BASE}/trade-images", timeout=5)
    data = r.json()
    check("GET /trade-images -> 200", r.status_code == 200)
    check("GET /trade-images -> []", isinstance(data, list) and len(data) == 0)
except Exception as e:
    check(f"GET /trade-images ({e})", False)
    check("GET /trade-images -> []", False)

# 4-8. GET /metrics -> 200 + key values
try:
    r = requests.get(f"{BASE}/metrics", timeout=5)
    check("GET /metrics -> 200", r.status_code == 200)
    m = r.json()
    check("total_trades == 0", m.get("total_trades") == 0)
    check("valid_setups == 0", m.get("valid_setups") == 0)
    check("invalid_setups == 0", m.get("invalid_setups") == 0)

    none_fields = [k for k, v in m.items() if not isinstance(v, (list, dict)) and v is None]
    check(f"no metric returns None (bad: {none_fields})", len(none_fields) == 0)
except Exception as e:
    check(f"GET /metrics ({e})", False)
    check("total_trades == 0", False)
    check("valid_setups == 0", False)
    check("invalid_setups == 0", False)
    check("no metric returns None", False)

print()
passed = sum(results)
total = len(results)
print(f"{'RESET PASS' if all(results) else 'RESET FAIL'} — {passed}/{total} checks passed")
