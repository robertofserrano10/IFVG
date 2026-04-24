import sys
import requests

BASE = "http://127.0.0.1:8000"
results = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append(condition)
    print(f"[{status}] {label}" + (f" — {detail}" if detail else ""))
    return condition


def run():
    print("=== Phase 13: trade images ===\n")

    # 1. Create trading day (prerequisite)
    r = requests.post(f"{BASE}/trading-days", json={
        "trade_date": "2026-04-24",
        "market": "NQ",
        "is_news_day": False,
        "is_ath_context": False,
    })
    if not check("POST /trading-days -> 201", r.status_code == 201, f"status={r.status_code}"):
        print("Abortando — no se pudo crear trading day.")
        return
    day_id = r.json()["id"]

    # 2. Create trade
    r = requests.post(f"{BASE}/trades", json={
        "trading_day_id":   day_id,
        "direction":        "long",
        "sweep_confirmed":  True,
        "ifvg_confirmed":   True,
        "vshape_confirmed": True,
        "smt_confirmed":    False,
        "entry_price":      19800.0,
        "stop_loss":        19750.0,
        "take_profit":      19900.0,
        "result_r":         2.0,
        "followed_rules":   True,
    })
    if not check("POST /trades -> 201", r.status_code == 201, f"status={r.status_code}"):
        print("Abortando — no se pudo crear trade.")
        return
    trade = r.json()
    trade_id = trade["id"]
    check("trade tiene campo 'id'", "id" in trade)

    # 3. Create trade image
    image_url = "https://example.com/chart_entrada.png"
    r = requests.post(f"{BASE}/trade-images", json={
        "trade_id":   trade_id,
        "image_url":  image_url,
        "image_type": "entrada",
    })
    if not check("POST /trade-images -> 201", r.status_code == 201, f"status={r.status_code}"):
        print(f"  Response: {r.text}")
        return
    img = r.json()
    check("imagen tiene trade_id correcto", img.get("trade_id") == trade_id)
    check("imagen tiene image_url correcto", img.get("image_url") == image_url)
    check("imagen tiene image_type 'entrada'", img.get("image_type") == "entrada")
    check("imagen tiene campo 'id'", "id" in img)
    check("imagen tiene campo 'created_at'", "created_at" in img)
    img_id = img["id"]

    # 4. GET /trade-images verifica que existe
    r = requests.get(f"{BASE}/trade-images")
    check("GET /trade-images -> 200", r.status_code == 200, f"status={r.status_code}")
    images = r.json()
    check("GET /trade-images retorna lista", isinstance(images, list))
    found = any(i["id"] == img_id for i in images)
    check("imagen creada aparece en GET /trade-images", found)

    # 5. Verify image linked to correct trade
    img_record = next((i for i in images if i["id"] == img_id), None)
    check("imagen vinculada al trade correcto", img_record and img_record["trade_id"] == trade_id)

    print()
    all_ok = all(results)
    print("RESULTADO FINAL:", "PASS" if all_ok else "FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    run()
