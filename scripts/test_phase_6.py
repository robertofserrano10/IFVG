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


def run():
    print("=== Phase 6: psychology fields in trades ===\n")

    day_id = get_first_trading_day_id()
    if day_id is None:
        return

    payload = {
        "trading_day_id": day_id,
        "direction": "long",
        "sweep_confirmed": True,
        "ifvg_confirmed": True,
        "vshape_confirmed": True,
        "smt_confirmed": False,
        "entry_price": 21000.0,
        "stop_loss": 20950.0,
        "take_profit": 21100.0,
        "followed_rules": True,
        "emotional_state": "calmado",
        "exit_reason": "por_plan",
    }

    r = requests.post(f"{BASE}/trades", json=payload)
    check("POST trade con campos psicologia -> 201", r.status_code == 201, f"status={r.status_code}")

    if r.status_code != 201:
        print("Abortando - POST fallido")
        return

    data = r.json()
    check("followed_rules presente y correcto", data.get("followed_rules") is True, f"got={data.get('followed_rules')}")
    check("emotional_state presente y correcto", data.get("emotional_state") == "calmado", f"got={data.get('emotional_state')}")
    check("exit_reason presente y correcto", data.get("exit_reason") == "por_plan", f"got={data.get('exit_reason')}")

    # POST con campos opcionales vacios
    payload_minimal = {
        "trading_day_id": day_id,
        "direction": "short",
        "sweep_confirmed": False,
        "ifvg_confirmed": False,
        "vshape_confirmed": False,
        "smt_confirmed": False,
        "entry_price": 21050.0,
        "stop_loss": 21100.0,
        "take_profit": 20900.0,
    }
    r2 = requests.post(f"{BASE}/trades", json=payload_minimal)
    check("POST trade sin campos psicologia -> 201", r2.status_code == 201, f"status={r2.status_code}")
    if r2.status_code == 201:
        d2 = r2.json()
        check("emotional_state es null cuando no se envia", d2.get("emotional_state") is None, f"got={d2.get('emotional_state')}")
        check("exit_reason es null cuando no se envia", d2.get("exit_reason") is None, f"got={d2.get('exit_reason')}")

    # GET verifica campos presentes
    r3 = requests.get(f"{BASE}/trades")
    trades = r3.json()
    if trades:
        check("followed_rules en GET /trades", "followed_rules" in trades[0], f"keys={list(trades[0].keys())}")
        check("emotional_state en GET /trades", "emotional_state" in trades[0])
        check("exit_reason en GET /trades", "exit_reason" in trades[0])

    print("\nDone.")


if __name__ == "__main__":
    run()
