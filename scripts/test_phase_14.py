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
    print("=== Phase 14: estrategia integrada — nuevos campos trades ===\n")

    # 1. Crear trading day
    r = requests.post(f"{BASE}/trading-days", json={
        "trade_date": "2026-04-24",
        "market": "NQ",
        "is_news_day": False,
        "is_ath_context": False,
    })
    if not check("POST /trading-days -> 201", r.status_code == 201, f"status={r.status_code}"):
        print("Abortando.")
        return
    day_id = r.json()["id"]

    # 2. Crear trade válido (todos los campos de estrategia)
    r = requests.post(f"{BASE}/trades", json={
        "trading_day_id":   day_id,
        "direction":        "long",
        "sweep_confirmed":  True,
        "pda_confirmed":    True,
        "ifvg_confirmed":   True,
        "vshape_confirmed": True,
        "smt_confirmed":    False,
        "clean_reaction":   True,
        "ny_killzone":      True,
        "liquidity_type":   "nwog",
        "entry_price":      19800.0,
        "stop_loss":        19750.0,
        "take_profit":      19900.0,
        "result_r":         2.0,
        "followed_rules":   True,
    })
    if not check("POST /trades (válido) -> 201", r.status_code == 201, f"status={r.status_code}"):
        print(f"  Response: {r.text}")
        return
    t = r.json()
    check("setup_valid=True cuando sweep+pda+ifvg+vshape confirmados", t.get("setup_valid") is True, f"got={t.get('setup_valid')}")
    check("pda_confirmed guardado", t.get("pda_confirmed") is True)
    check("liquidity_type='nwog' guardado", t.get("liquidity_type") == "nwog", f"got={t.get('liquidity_type')}")
    check("clean_reaction guardado", t.get("clean_reaction") is True)
    check("ny_killzone guardado", t.get("ny_killzone") is True)
    check("discipline_label='Trade disciplinado'", t.get("discipline_label") == "Trade disciplinado", f"got={t.get('discipline_label')}")

    # 3. Crear trade inválido por falta PDA
    r = requests.post(f"{BASE}/trades", json={
        "trading_day_id":   day_id,
        "direction":        "short",
        "sweep_confirmed":  True,
        "pda_confirmed":    False,
        "ifvg_confirmed":   True,
        "vshape_confirmed": True,
        "smt_confirmed":    False,
        "clean_reaction":   False,
        "ny_killzone":      False,
        "liquidity_type":   None,
        "entry_price":      19800.0,
        "stop_loss":        19850.0,
        "take_profit":      19700.0,
    })
    if not check("POST /trades (sin PDA) -> 201", r.status_code == 201, f"status={r.status_code}"):
        print(f"  Response: {r.text}")
        return
    t2 = r.json()
    check("setup_valid=False cuando pda_confirmed=False", t2.get("setup_valid") is False, f"got={t2.get('setup_valid')}")
    check("discipline_label indica faltó PDA HTF", t2.get("discipline_label") == "Setup inválido: faltó PDA HTF", f"got={t2.get('discipline_label')}")

    # 4. GET /trades verifica campos nuevos presentes
    r = requests.get(f"{BASE}/trades")
    check("GET /trades -> 200", r.status_code == 200, f"status={r.status_code}")
    trades = r.json()
    check("GET /trades retorna lista no vacía", len(trades) > 0)
    sample = trades[0]
    check("campo pda_confirmed presente en GET", "pda_confirmed" in sample)
    check("campo liquidity_type presente en GET", "liquidity_type" in sample)
    check("campo clean_reaction presente en GET", "clean_reaction" in sample)
    check("campo ny_killzone presente en GET", "ny_killzone" in sample)

    # 5. Verificar que el trade válido tiene liquidity_type="nwog"
    valido = next((t for t in trades if t.get("liquidity_type") == "nwog"), None)
    check("trade con liquidity_type='nwog' encontrado en GET", valido is not None)

    print()
    all_ok = all(results)
    print("RESULTADO FINAL:", "PASS" if all_ok else "FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    run()
