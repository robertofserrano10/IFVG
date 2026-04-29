import requests

BASE = "http://127.0.0.1:8000"

results = []

def check(label, ok):
    print(f"{'PASS' if ok else 'FAIL'} - {label}")
    results.append(ok)
    return ok


# ── 1. Create trading day ────────────────────────────────────────────────────
try:
    r = requests.post(f"{BASE}/trading-days", json={
        "trade_date": "2099-12-01", "market": "NQ",
        "is_news_day": False, "is_ath_context": False
    }, timeout=5)
    check("Create trading day -> 201", r.status_code == 201)
    day_id = r.json().get("id")
except Exception as e:
    check(f"Create trading day (error: {e})", False)
    day_id = None

# ── 2. Create trade ──────────────────────────────────────────────────────────
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

# ── 3. Create trade_image record ─────────────────────────────────────────────
try:
    r = requests.post(f"{BASE}/trade-images", json={
        "trade_id": trade_id,
        "image_url": "https://example.com/test.png",
        "image_type": "entrada",
    }, timeout=5)
    check("Create trade_image -> 201", r.status_code == 201)
except Exception as e:
    check(f"Create trade_image (error: {e})", False)

# ── 4. GET /trades contains the trade ────────────────────────────────────────
try:
    r = requests.get(f"{BASE}/trades", timeout=5)
    ids = [t["id"] for t in r.json()]
    check("GET /trades contains created trade", trade_id in ids)
except Exception as e:
    check(f"GET /trades contains created trade (error: {e})", False)

# ── 5. DELETE /trades/{id} ────────────────────────────────────────────────────
try:
    r = requests.delete(f"{BASE}/trades/{trade_id}", timeout=5)
    check("DELETE /trades/{id} -> 200", r.status_code == 200)
    body = r.json()
    check("Response deleted=true", body.get("deleted") is True)
    check("Response trade_id matches", body.get("trade_id") == trade_id)
except Exception as e:
    check(f"DELETE /trades/{trade_id} (error: {e})", False)

# ── 6. GET /trades no longer contains the trade ──────────────────────────────
try:
    r = requests.get(f"{BASE}/trades", timeout=5)
    ids = [t["id"] for t in r.json()]
    check("GET /trades no longer contains deleted trade", trade_id not in ids)
except Exception as e:
    check(f"GET /trades after delete (error: {e})", False)

# ── 7. GET /trade-images no longer contains images for that trade ────────────
try:
    r = requests.get(f"{BASE}/trade-images", timeout=5)
    imgs = [i for i in r.json() if i.get("trade_id") == trade_id]
    check("GET /trade-images no images for deleted trade", len(imgs) == 0)
except Exception as e:
    check(f"GET /trade-images after delete (error: {e})", False)

# ── 8. DELETE /trades/999999 -> 404 ──────────────────────────────────────────
try:
    r = requests.delete(f"{BASE}/trades/999999", timeout=5)
    check("DELETE /trades/999999 -> 404", r.status_code == 404)
except Exception as e:
    check(f"DELETE /trades/999999 (error: {e})", False)

# ── 9. GET /metrics still responds 200 ───────────────────────────────────────
try:
    r = requests.get(f"{BASE}/metrics", timeout=5)
    check("GET /metrics -> 200 after delete", r.status_code == 200)
except Exception as e:
    check(f"GET /metrics (error: {e})", False)

# ── 10. Frontend checks ───────────────────────────────────────────────────────
try:
    with open("frontend/app.js", "r", encoding="utf-8") as f:
        js = f.read()
    check("frontend/app.js contains DELETE fetch call", 'method: "DELETE"' in js)
    check("frontend/app.js contains confirmation text", "This action cannot be undone" in js)
except Exception as e:
    check(f"frontend checks (error: {e})", False)


# ── Summary ───────────────────────────────────────────────────────────────────
total = len(results)
passed = sum(results)
print(f"\n{'FASE 27 PASS' if passed == total else 'FASE 27 FAIL'} ({passed}/{total})")
