import requests
from datetime import date

BASE = "http://127.0.0.1:8000"
JS_PATH = "frontend/app.js"

results = []

def check(label, ok):
    print(f"{'PASS' if ok else 'FAIL'} - {label}")
    results.append(ok)
    return ok


# ── 1. Create trading day ─────────────────────────────────────────────────────
try:
    r = requests.post(f"{BASE}/trading-days", json={
        "trade_date": "2099-11-01", "market": "NQ",
        "is_news_day": False, "is_ath_context": False
    }, timeout=5)
    check("Create trading day -> 201", r.status_code == 201)
    day_id = r.json().get("id")
except Exception as e:
    check(f"Create trading day (error: {e})", False)
    day_id = None

# ── 2. Create daily bias ──────────────────────────────────────────────────────
bias_id = None
try:
    r = requests.post(f"{BASE}/daily-bias", json={
        "trading_day_id": day_id or 1,
        "bias_direction": "bullish",
        "bias_alignment": True,
        "bias_active": True,
        "chop_equilibrium": False,
        "invalidated": False,
        "daily_high": 21100.0, "daily_low": 20900.0, "daily_eq": 21000.0,
        "current_price": 21000.0, "zone_position": "none",
        "asia_high": 21050.0, "asia_low": 20950.0,
        "london_high": 21080.0, "london_low": 20980.0,
        "pending_liquidity_direction": "none", "premium_discount_direction": "none",
    }, timeout=5)
    check("Create daily bias -> 201", r.status_code == 201)
    bias_id = r.json().get("id")
except Exception as e:
    check(f"Create daily bias (error: {e})", False)

# ── 3. Create trade ───────────────────────────────────────────────────────────
trade_id = None
try:
    r = requests.post(f"{BASE}/trades", json={
        "trading_day_id": day_id or 1,
        "direction": "long",
        "entry_price": 21000.0,
        "stop_loss": 20950.0,
        "take_profit": 21100.0,
    }, timeout=5)
    check("Create trade -> 201", r.status_code == 201)
    trade_id = r.json().get("id")
except Exception as e:
    check(f"Create trade (error: {e})", False)

# ── 4. Create trade_image ─────────────────────────────────────────────────────
try:
    r = requests.post(f"{BASE}/trade-images", json={
        "trade_id": trade_id,
        "image_url": "https://example.com/test30.png",
        "image_type": "entrada",
    }, timeout=5)
    check("Create trade_image -> 201", r.status_code == 201)
except Exception as e:
    check(f"Create trade_image (error: {e})", False)

# ── 5. DELETE /daily-bias/{bias_id} -> 200 ───────────────────────────────────
try:
    r = requests.delete(f"{BASE}/daily-bias/{bias_id}", timeout=5)
    check("DELETE /daily-bias/{id} -> 200", r.status_code == 200)
    body = r.json()
    check("daily bias response deleted=true", body.get("deleted") is True)
    check("daily bias response id matches", body.get("daily_bias_id") == bias_id)
except Exception as e:
    check(f"DELETE /daily-bias (error: {e})", False)

# ── 6. DELETE /daily-bias/999999 -> 404 ──────────────────────────────────────
try:
    r = requests.delete(f"{BASE}/daily-bias/999999", timeout=5)
    check("DELETE /daily-bias/999999 -> 404", r.status_code == 404)
except Exception as e:
    check(f"DELETE /daily-bias/999999 (error: {e})", False)

# ── 7. Create second trading day with trade/bias/image ────────────────────────
day2_id = trade2_id = None
try:
    r = requests.post(f"{BASE}/trading-days", json={
        "trade_date": "2099-11-02", "market": "ES",
        "is_news_day": False, "is_ath_context": False
    }, timeout=5)
    check("Create second trading day -> 201", r.status_code == 201)
    day2_id = r.json().get("id")
except Exception as e:
    check(f"Create second trading day (error: {e})", False)

try:
    r = requests.post(f"{BASE}/daily-bias", json={
        "trading_day_id": day2_id or 1,
        "bias_direction": "bearish",
        "bias_alignment": True,
        "bias_active": True,
        "chop_equilibrium": False,
        "invalidated": False,
        "daily_high": 5100.0, "daily_low": 4900.0, "daily_eq": 5000.0,
        "current_price": 5000.0, "zone_position": "none",
        "asia_high": 5050.0, "asia_low": 4950.0,
        "london_high": 5080.0, "london_low": 4980.0,
        "pending_liquidity_direction": "none", "premium_discount_direction": "none",
    }, timeout=5)
    check("Create bias for second day -> 201", r.status_code == 201)
except Exception as e:
    check(f"Create bias for second day (error: {e})", False)

try:
    r = requests.post(f"{BASE}/trades", json={
        "trading_day_id": day2_id or 1,
        "direction": "short",
        "entry_price": 5000.0,
        "stop_loss": 5020.0,
        "take_profit": 4970.0,
    }, timeout=5)
    check("Create trade for second day -> 201", r.status_code == 201)
    trade2_id = r.json().get("id")
except Exception as e:
    check(f"Create trade for second day (error: {e})", False)

try:
    r = requests.post(f"{BASE}/trade-images", json={
        "trade_id": trade2_id,
        "image_url": "https://example.com/test30b.png",
        "image_type": "salida",
    }, timeout=5)
    check("Create trade_image for second day -> 201", r.status_code == 201)
except Exception as e:
    check(f"Create trade_image for second day (error: {e})", False)

# ── 8. DELETE /trading-days/{day2_id} -> 200 ─────────────────────────────────
try:
    r = requests.delete(f"{BASE}/trading-days/{day2_id}", timeout=5)
    check("DELETE /trading-days/{id} -> 200", r.status_code == 200)
    body = r.json()
    check("trading day response deleted=true", body.get("deleted") is True)
    check("trading day response id matches", body.get("trading_day_id") == day2_id)
except Exception as e:
    check(f"DELETE /trading-days (error: {e})", False)

# ── 9. trading_day gone ───────────────────────────────────────────────────────
try:
    r = requests.get(f"{BASE}/trading-days", timeout=5)
    ids = [d["id"] for d in r.json()]
    check("Deleted trading day no longer in GET /trading-days", day2_id not in ids)
except Exception as e:
    check(f"GET /trading-days after delete (error: {e})", False)

# ── 10. trades gone ───────────────────────────────────────────────────────────
try:
    r = requests.get(f"{BASE}/trades", timeout=5)
    ids = [t["id"] for t in r.json()]
    check("Related trade no longer in GET /trades", trade2_id not in ids)
except Exception as e:
    check(f"GET /trades after delete (error: {e})", False)

# ── 11. trade_images gone ─────────────────────────────────────────────────────
try:
    r = requests.get(f"{BASE}/trade-images", timeout=5)
    imgs = [i for i in r.json() if i.get("trade_id") == trade2_id]
    check("Related trade_images gone after trading day delete", len(imgs) == 0)
except Exception as e:
    check(f"GET /trade-images after delete (error: {e})", False)

# ── 12. DELETE /trading-days/999999 -> 404 ───────────────────────────────────
try:
    r = requests.delete(f"{BASE}/trading-days/999999", timeout=5)
    check("DELETE /trading-days/999999 -> 404", r.status_code == 404)
except Exception as e:
    check(f"DELETE /trading-days/999999 (error: {e})", False)

# ── 13. /metrics still 200 ────────────────────────────────────────────────────
try:
    r = requests.get(f"{BASE}/metrics", timeout=5)
    check("GET /metrics -> 200 after deletes", r.status_code == 200)
except Exception as e:
    check(f"GET /metrics (error: {e})", False)

# ── 14-15. Frontend checks ────────────────────────────────────────────────────
try:
    with open(JS_PATH, "r", encoding="utf-8") as f:
        js = f.read()
    check("frontend/app.js contains Delete Day", "Delete Day" in js)
    check("frontend/app.js contains Delete Bias", "Delete Bias" in js)
except Exception as e:
    check(f"frontend checks (error: {e})", False)


# ── Summary ───────────────────────────────────────────────────────────────────
total = len(results)
passed = sum(results)
print(f"\n{'FASE 30 PASS' if passed == total else 'FASE 30 FAIL'} ({passed}/{total})")
