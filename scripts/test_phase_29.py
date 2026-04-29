import re
from datetime import date
import requests

BASE = "http://127.0.0.1:8000"
HTML_PATH = "frontend/index.html"
JS_PATH   = "frontend/app.js"

results = []

def check(label, ok):
    print(f"{'PASS' if ok else 'FAIL'} - {label}")
    results.append(ok)
    return ok


with open(HTML_PATH, "r", encoding="utf-8") as f:
    html = f.read()

with open(JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()


# ── HTML checks ───────────────────────────────────────────────────────────────

check("index.html has input type=date", 'type="date"' in html)
check("index.html has trade_date field", 'id="trade_date"' in html)
check("index.html date label mentions defaults to today", "defaults to today" in html)

# ── JS checks ─────────────────────────────────────────────────────────────────

check("app.js sets today date on DOMContentLoaded", "setTodayDate" in js)
check("app.js todayISO function exists", "todayISO" in js)
check("app.js re-sets date after form reset", js.count("setTodayDate") >= 2)
check("app.js auto-selects trading day in trade form", "trade_trading_day_id" in js and "days[0].id" in js)
check("app.js saveTradingDay still exists", "saveTradingDay" in js)
check("app.js saveTrade still exists", "saveTrade" in js)
check("app.js uses YYYY-MM-DD format for date input", "getFullYear" in js and "getMonth" in js and "getDate" in js)

# ── API smoke tests ───────────────────────────────────────────────────────────

today = date.today().isoformat()

try:
    r = requests.get(f"{BASE}/trading-days", timeout=5)
    check("GET /trading-days -> 200", r.status_code == 200)
except Exception as e:
    check(f"GET /trading-days (error: {e})", False)

try:
    r = requests.post(f"{BASE}/trading-days", json={
        "trade_date": today, "market": "NQ",
        "is_news_day": False, "is_ath_context": False
    }, timeout=5)
    check("POST /trading-days -> 201", r.status_code == 201)
    day_id = r.json().get("id") if r.status_code == 201 else None
except Exception as e:
    check(f"POST /trading-days (error: {e})", False)
    day_id = None

try:
    r = requests.post(f"{BASE}/trades", json={
        "trading_day_id": day_id or 1,
        "direction": "long",
        "entry_price": 21000.0,
        "stop_loss": 20950.0,
        "take_profit": 21100.0,
    }, timeout=5)
    check("POST /trades -> 201", r.status_code == 201)
except Exception as e:
    check(f"POST /trades (error: {e})", False)


# ── Summary ───────────────────────────────────────────────────────────────────
total = len(results)
passed = sum(results)
print(f"\n{'FASE 29 PASS' if passed == total else 'FASE 29 FAIL'} ({passed}/{total})")
