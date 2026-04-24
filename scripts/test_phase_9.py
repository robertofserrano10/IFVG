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
        print("[SKIP] No hay trading days - crea uno primero")
        return None
    return days[0]["id"]


def post_trade(day_id, overrides=None):
    payload = {
        "trading_day_id": day_id,
        "direction": "long",
        "sweep_confirmed": True,
        "ifvg_confirmed": True,
        "vshape_confirmed": True,
        "entry_price": 21000.0,
        "stop_loss": 20950.0,
        "take_profit": 21100.0,
    }
    if overrides:
        payload.update(overrides)
    r = requests.post(f"{BASE}/trades", json=payload)
    if r.status_code == 201:
        return r.json()
    print(f"  POST fallido: {r.status_code} {r.text}")
    return None


def find_in_get(trade_id):
    trades = requests.get(f"{BASE}/trades").json()
    return next((t for t in trades if t["id"] == trade_id), None)


def run():
    print("=== Phase 9: discipline/psychology labels ===\n")

    day_id = get_first_trading_day_id()
    if not day_id:
        return

    # 1. Trade disciplinado
    t = post_trade(day_id, {"followed_rules": True})
    if t:
        found = find_in_get(t["id"])
        got = found.get("discipline_label") if found else None
        check("discipline_label = 'Trade disciplinado'", got == "Trade disciplinado", f"got={got}")

    # 2. Error de disciplina
    t = post_trade(day_id, {"followed_rules": False})
    if t:
        found = find_in_get(t["id"])
        got = found.get("discipline_label") if found else None
        check("discipline_label = 'Error de disciplina'", got == "Error de disciplina", f"got={got}")

    # 3. Setup invalido (vshape OFF -> setup_valid=False)
    t = post_trade(day_id, {"vshape_confirmed": False, "followed_rules": True})
    if t:
        found = find_in_get(t["id"])
        got = found.get("discipline_label") if found else None
        check("discipline_label = Setup invalido cuando setup_valid=False", got is not None and got not in ("Trade disciplinado", "Error de disciplina"), f"got={got}")

    # 4. FOMO
    t = post_trade(day_id, {"followed_rules": True, "emotional_state": "fomo"})
    if t:
        found = find_in_get(t["id"])
        got = found.get("emotional_label") if found else None
        check("emotional_label = 'Trade emocional (FOMO)'", got == "Trade emocional (FOMO)", f"got={got}")

    # 5. Salida por miedo
    t = post_trade(day_id, {"followed_rules": True, "exit_reason": "por_miedo"})
    if t:
        found = find_in_get(t["id"])
        got = found.get("exit_label") if found else None
        check("exit_label = 'Salida por miedo'", got == "Salida por miedo", f"got={got}")

    # 6. Labels presentes en GET /trades
    trades = requests.get(f"{BASE}/trades").json()
    if trades:
        t0 = trades[0]
        check("discipline_label en GET /trades", "discipline_label" in t0)
        check("emotional_label en GET /trades", "emotional_label" in t0)
        check("exit_label en GET /trades", "exit_label" in t0)

    print("\nDone.")


if __name__ == "__main__":
    run()
