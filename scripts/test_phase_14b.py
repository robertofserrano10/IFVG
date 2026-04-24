import sys
import requests

BASE = "http://127.0.0.1:8000"
results = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append(condition)
    print(f"[{status}] {label}" + (f" — {detail}" if detail else ""))
    return condition


def post_trade(day_id, overrides=None):
    base = {
        "trading_day_id":   day_id,
        "direction":        "long",
        "sweep_confirmed":  False,
        "pda_confirmed":    False,
        "ifvg_confirmed":   False,
        "vshape_confirmed": False,
        "smt_confirmed":    False,
        "clean_reaction":   False,
        "ny_killzone":      False,
        "liquidity_type":   None,
        "entry_price":      19800.0,
        "stop_loss":        19750.0,
        "take_profit":      19900.0,
    }
    if overrides:
        base.update(overrides)
    return requests.post(f"{BASE}/trades", json=base)


def run():
    print("=== Phase 14B: detección automática de errores ===\n")

    # Setup: trading day
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

    # ── Trade A+ ─────────────────────────────────────────────────────────────
    r = post_trade(day_id, {
        "sweep_confirmed":  True,
        "pda_confirmed":    True,
        "ifvg_confirmed":   True,
        "vshape_confirmed": True,
        "clean_reaction":   True,
        "ny_killzone":      True,
        "followed_rules":   True,
    })
    check("Trade A+ -> 201", r.status_code == 201, f"status={r.status_code}")
    t = r.json()
    check("A+: technical_error_label correcto",    t.get("technical_error_label")  == "Sin error técnico crítico",    f"got={t.get('technical_error_label')}")
    check("A+: psychology_error_label correcto",   t.get("psychology_error_label") == "Sin error psicológico crítico",f"got={t.get('psychology_error_label')}")
    check("A+: execution_quality_label correcto",  t.get("execution_quality_label")== "Ejecución A+",                 f"got={t.get('execution_quality_label')}")
    check("A+: trade_grade='A+'",                  t.get("trade_grade")            == "A+",                          f"got={t.get('trade_grade')}")

    # ── Trade sin sweep ───────────────────────────────────────────────────────
    r = post_trade(day_id, {
        "sweep_confirmed":  False,
        "pda_confirmed":    True,
        "ifvg_confirmed":   True,
        "vshape_confirmed": True,
    })
    check("Trade sin sweep -> 201", r.status_code == 201, f"status={r.status_code}")
    t = r.json()
    check("Sin sweep: technical_error_label correcto", t.get("technical_error_label") == "Error técnico: entrada sin sweep", f"got={t.get('technical_error_label')}")

    # ── Trade sin IFVG ────────────────────────────────────────────────────────
    r = post_trade(day_id, {
        "sweep_confirmed":  True,
        "pda_confirmed":    True,
        "ifvg_confirmed":   False,
        "vshape_confirmed": True,
    })
    check("Trade sin IFVG -> 201", r.status_code == 201, f"status={r.status_code}")
    t = r.json()
    check("Sin IFVG: technical_error_label correcto", t.get("technical_error_label") == "Error técnico: entrada sin IFVG", f"got={t.get('technical_error_label')}")

    # ── Trade con FOMO ────────────────────────────────────────────────────────
    r = post_trade(day_id, {
        "sweep_confirmed":  True,
        "pda_confirmed":    True,
        "ifvg_confirmed":   True,
        "vshape_confirmed": True,
        "emotional_state":  "fomo",
        "followed_rules":   True,
        "clean_reaction":   True,
        "ny_killzone":      True,
    })
    check("Trade con FOMO -> 201", r.status_code == 201, f"status={r.status_code}")
    t = r.json()
    check("FOMO: psychology_error_label correcto", t.get("psychology_error_label") == "Error psicológico: FOMO", f"got={t.get('psychology_error_label')}")

    # ── Trade setup válido + followed_rules=false ─────────────────────────────
    r = post_trade(day_id, {
        "sweep_confirmed":  True,
        "pda_confirmed":    True,
        "ifvg_confirmed":   True,
        "vshape_confirmed": True,
        "followed_rules":   False,
    })
    check("Trade válido followed_rules=false -> 201", r.status_code == 201, f"status={r.status_code}")
    t = r.json()
    check("Bad discipline: execution_quality_label correcto", t.get("execution_quality_label") == "Setup válido con mala disciplina", f"got={t.get('execution_quality_label')}")
    check("Bad discipline: trade_grade='B'",                  t.get("trade_grade")             == "B",                              f"got={t.get('trade_grade')}")

    # ── GET /trades — nuevos campos presentes ─────────────────────────────────
    r = requests.get(f"{BASE}/trades")
    check("GET /trades -> 200", r.status_code == 200, f"status={r.status_code}")
    trades = r.json()
    check("GET devuelve lista no vacía", len(trades) > 0)
    s = trades[0]
    check("campo technical_error_label en GET",   "technical_error_label"   in s)
    check("campo psychology_error_label en GET",  "psychology_error_label"  in s)
    check("campo execution_quality_label en GET", "execution_quality_label" in s)
    check("campo trade_grade en GET",             "trade_grade"             in s)

    print()
    all_ok = all(results)
    print("RESULTADO FINAL:", "FASE 14B PASS" if all_ok else "FASE 14B FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    run()
