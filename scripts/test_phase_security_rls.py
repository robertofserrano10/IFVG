import subprocess
import requests

BASE = "http://127.0.0.1:8000"

FRONTEND_FILES = [
    "frontend/config.js",
    "frontend/app.js",
]

BACKEND_ENV = "backend/.env"

results = []

def check(label, ok):
    print(f"{'PASS' if ok else 'FAIL'} - {label}")
    results.append(ok)
    return ok


# ── API smoke tests ──────────────────────────────────────────────────────────

# GET /health
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    check("GET /health -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /health -> 200 (error: {e})", False)

# POST /trading-days
try:
    payload = {"trade_date": "2099-01-01", "market": "NQ", "is_news_day": False, "is_ath_context": False}
    r = requests.post(f"{BASE}/trading-days", json=payload, timeout=5)
    check("POST /trading-days -> 201", r.status_code == 201)
    created_day_id = r.json().get("id") if r.status_code == 201 else None
except Exception as e:
    check(f"POST /trading-days -> 201 (error: {e})", False)
    created_day_id = None

# POST /trades
try:
    day_id = created_day_id or 1
    payload = {
        "trading_day_id": day_id,
        "direction": "long",
        "entry_price": 21000.0,
        "stop_loss": 20950.0,
        "take_profit": 21100.0,
        "followed_rules": True,
        "emotional_state": "calm",
        "exit_reason": "target",
    }
    r = requests.post(f"{BASE}/trades", json=payload, timeout=5)
    check("POST /trades -> 201", r.status_code == 201)
    created_trade_id = r.json().get("id") if r.status_code == 201 else None
except Exception as e:
    check(f"POST /trades -> 201 (error: {e})", False)
    created_trade_id = None

# GET /trades
try:
    r = requests.get(f"{BASE}/trades", timeout=5)
    check("GET /trades -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /trades -> 200 (error: {e})", False)

# GET /metrics
try:
    r = requests.get(f"{BASE}/metrics", timeout=5)
    check("GET /metrics -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /metrics -> 200 (error: {e})", False)

# POST /trade-images/upload — validation error (no file)
try:
    r = requests.post(f"{BASE}/trade-images/upload", timeout=5)
    check("POST /trade-images/upload returns error on missing file", r.status_code in (400, 422))
except Exception as e:
    check(f"POST /trade-images/upload error validation (error: {e})", False)


# ── Security checks ──────────────────────────────────────────────────────────

# Frontend must NOT contain service_role
for fpath in FRONTEND_FILES:
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        check(f"{fpath} does not contain service_role", "service_role" not in content.lower())
    except FileNotFoundError:
        check(f"{fpath} exists", False)

# backend/.env not tracked by git
try:
    result = subprocess.run(
        ["git", "ls-files", BACKEND_ENV],
        capture_output=True, text=True
    )
    check("backend/.env not tracked by git", result.stdout.strip() == "")
except Exception as e:
    check(f"backend/.env git check (error: {e})", False)


# ── Summary ──────────────────────────────────────────────────────────────────

total = len(results)
passed = sum(results)
print(f"\n{'SECURITY RLS PASS' if passed == total else 'SECURITY RLS FAIL'} ({passed}/{total})")
