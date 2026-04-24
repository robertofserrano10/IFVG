import requests

BASE = "http://127.0.0.1:8000"

def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" - {detail}" if detail else ""))
    return condition


def get_first_trading_day_id():
    r = requests.get(f"{BASE}/trading-days")
    days = r.json()
    if not days:
        print("[SKIP] No hay trading days — crea uno primero")
        return None
    return days[0]["id"]


def run():
    print("=== Phase 5: trades + setup_valid ===\n")

    # 1. GET /trades responds
    r = requests.get(f"{BASE}/trades")
    check("GET /trades responde 200", r.status_code == 200, f"status={r.status_code}")

    day_id = get_first_trading_day_id()
    if day_id is None:
        return

    # 2. POST trade with all three flags ON → setup_valid must be True
    payload_valid = {
        "trading_day_id": day_id,
        "direction": "long",
        "sweep_confirmed": True,
        "ifvg_confirmed": True,
        "vshape_confirmed": True,
        "smt_confirmed": False,
        "entry_price": 21000.0,
        "stop_loss": 20950.0,
        "take_profit": 21100.0,
    }
    r = requests.post(f"{BASE}/trades", json=payload_valid)
    check("POST trade (flags ON) -> 201", r.status_code == 201, f"status={r.status_code}")
    if r.status_code == 201:
        data = r.json()
        check("setup_valid=True cuando sweep+ifvg+vshape ON", data.get("setup_valid") is True, f"got={data.get('setup_valid')}")

    # 3. POST trade with one flag OFF → setup_valid must be False
    payload_invalid = {**payload_valid, "ifvg_confirmed": False}
    r = requests.post(f"{BASE}/trades", json=payload_invalid)
    check("POST trade (ifvg OFF) -> 201", r.status_code == 201, f"status={r.status_code}")
    if r.status_code == 201:
        data = r.json()
        check("setup_valid=False cuando ifvg OFF", data.get("setup_valid") is False, f"got={data.get('setup_valid')}")

    # 4. GET /trades returns setup_valid field
    r = requests.get(f"{BASE}/trades")
    trades = r.json()
    if trades:
        check("setup_valid presente en GET /trades", "setup_valid" in trades[0], f"keys={list(trades[0].keys())}")

    print("\nDone.")


if __name__ == "__main__":
    run()
