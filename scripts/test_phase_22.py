import datetime
import requests

BASE  = "http://127.0.0.1:8000"
# Use a future month so the DB has no prior trades for it
TEST_DATE = datetime.date(2099, 11, 15)
YEAR      = TEST_DATE.year
MONTH     = TEST_DATE.month

# Small reliable public JPEG for happy-path test
GOOD_IMG_URL = "https://httpbin.org/image/jpeg"
# Unreachable URL for fail-safe test
BAD_IMG_URL  = "http://127.0.0.1:59999/nonexistent.jpg"

results = []


def check(label, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}" + (f" — {detail}" if detail else ""))
    results.append(ok)
    return ok


# ── Setup: create test data ────────────────────────────────────────────────

# 1. Create trading day
td_resp = requests.post(f"{BASE}/trading-days", json={
    "trade_date": TEST_DATE.isoformat(),
    "market": "NQ",
    "is_news_day": False,
    "is_ath_context": False,
    "notes": "test_phase_22",
}, timeout=10)
if not check("Crear trading day", td_resp.status_code == 201, str(td_resp.status_code)):
    print("FASE 22 FAIL — no se pudo crear trading day")
    raise SystemExit(1)
day_id = td_resp.json()["id"]

# 2. Create trade
tr_resp = requests.post(f"{BASE}/trades", json={
    "trading_day_id":   day_id,
    "daily_bias_id":    None,
    "direction":        "long",
    "sweep_confirmed":  True,
    "pda_confirmed":    True,
    "ifvg_confirmed":   True,
    "vshape_confirmed": True,
    "smt_confirmed":    False,
    "clean_reaction":   True,
    "ny_killzone":      True,
    "liquidity_type":   "pdh",
    "entry_price":      17500.0,
    "stop_loss":        17480.0,
    "take_profit":      17560.0,
    "result_r":         2.0,
    "notes":            "test_phase_22",
    "followed_rules":   True,
    "emotional_state":  "calmado",
    "exit_reason":      "por_plan",
}, timeout=10)
if not check("Crear trade", tr_resp.status_code == 201, str(tr_resp.status_code)):
    print("FASE 22 FAIL — no se pudo crear trade")
    raise SystemExit(1)
trade_id = tr_resp.json()["id"]

# 3. Create trade_image with good URL
gi_resp = requests.post(f"{BASE}/trade-images", json={
    "trade_id":   trade_id,
    "image_url":  GOOD_IMG_URL,
    "image_type": "entrada",
}, timeout=10)
check("Crear trade_image (URL válida)", gi_resp.status_code == 201, str(gi_resp.status_code))

# 4. Create trade_image with bad URL (fail-safe test data)
bi_resp = requests.post(f"{BASE}/trade-images", json={
    "trade_id":   trade_id,
    "image_url":  BAD_IMG_URL,
    "image_type": "contexto",
}, timeout=10)
check("Crear trade_image (URL inválida)", bi_resp.status_code == 201, str(bi_resp.status_code))

# ── Test 5: PDF sin imágenes (baseline) ───────────────────────────────────

r_no_img = requests.get(
    f"{BASE}/reports/monthly/pdf",
    params={"year": YEAR, "month": MONTH, "include_images": "false"},
    timeout=30,
)
check("PDF sin imágenes — status 200", r_no_img.status_code == 200, str(r_no_img.status_code))
check("PDF sin imágenes — Content-Type PDF",
      "pdf" in r_no_img.headers.get("content-type", "").lower())
check("PDF sin imágenes — empieza con %PDF",
      r_no_img.content[:4] == b"%PDF")
size_no_img = len(r_no_img.content)

# ── Test 6: PDF con imágenes ──────────────────────────────────────────────

r_with_img = requests.get(
    f"{BASE}/reports/monthly/pdf",
    params={"year": YEAR, "month": MONTH, "include_images": "true"},
    timeout=60,
)
check("PDF con imágenes — status 200", r_with_img.status_code == 200, str(r_with_img.status_code))
check("PDF con imágenes — Content-Type PDF",
      "pdf" in r_with_img.headers.get("content-type", "").lower())
check("PDF con imágenes — empieza con %PDF",
      r_with_img.content[:4] == b"%PDF")
size_with_img = len(r_with_img.content)
check(
    f"PDF con imágenes — mayor que sin imágenes ({size_with_img} > {size_no_img})",
    size_with_img > size_no_img,
)

# ── Test 7: Fail-safe — imagen inválida no rompe PDF ──────────────────────

# Create a second trade with only a bad URL image
tr2_resp = requests.post(f"{BASE}/trades", json={
    "trading_day_id":  day_id,
    "direction":       "short",
    "sweep_confirmed": False,
    "pda_confirmed":   False,
    "ifvg_confirmed":  False,
    "vshape_confirmed":False,
    "smt_confirmed":   False,
    "clean_reaction":  False,
    "ny_killzone":     False,
    "entry_price":     17500.0,
    "stop_loss":       17520.0,
    "take_profit":     17440.0,
    "result_r":        -1.0,
    "followed_rules":  False,
    "notes":           "test_phase_22_bad_img",
}, timeout=10)
if tr2_resp.status_code == 201:
    trade2_id = tr2_resp.json()["id"]
    requests.post(f"{BASE}/trade-images", json={
        "trade_id":   trade2_id,
        "image_url":  BAD_IMG_URL,
        "image_type": "entrada",
    }, timeout=10)

r_bad = requests.get(
    f"{BASE}/reports/monthly/pdf",
    params={"year": YEAR, "month": MONTH, "include_images": "true"},
    timeout=60,
)
check("Fail-safe imagen rota — no crash (status 200)", r_bad.status_code == 200, str(r_bad.status_code))
check("Fail-safe imagen rota — sigue siendo PDF",
      r_bad.content[:4] == b"%PDF")

# ── Summary ───────────────────────────────────────────────────────────────

passed = sum(results)
total  = len(results)
print(f"\n{'='*40}")
print(f"FASE 22: {passed}/{total} checks pasaron")
if passed == total:
    print("FASE 22 PASS")
else:
    print("FASE 22 FAIL")
