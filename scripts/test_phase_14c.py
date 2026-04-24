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
    r = requests.post(f"{BASE}/trades", json=base)
    if r.status_code != 201:
        print(f"  [WARN] POST /trades status={r.status_code}: {r.text[:120]}")
    return r


def run():
    print("=== Phase 14C: métricas por errores ===\n")

    # ── Setup ─────────────────────────────────────────────────────────────────
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

    # ── Crear trades controlados ──────────────────────────────────────────────

    # 1. A+ (grade A+)
    post_trade(day_id, {
        "sweep_confirmed": True, "pda_confirmed": True,
        "ifvg_confirmed": True, "vshape_confirmed": True,
        "clean_reaction": True, "ny_killzone": True, "followed_rules": True,
    })

    # 2. Sin sweep (grade C — setup inválido + followed_rules=True)
    post_trade(day_id, {
        "sweep_confirmed": False, "pda_confirmed": True,
        "ifvg_confirmed": True, "vshape_confirmed": True,
        "followed_rules": True,
    })

    # 3. Sin PDA (grade F)
    post_trade(day_id, {
        "sweep_confirmed": True, "pda_confirmed": False,
        "ifvg_confirmed": True, "vshape_confirmed": True,
    })

    # 4. Sin IFVG (grade F)
    post_trade(day_id, {
        "sweep_confirmed": True, "pda_confirmed": True,
        "ifvg_confirmed": False, "vshape_confirmed": True,
    })

    # 5. Sin V-Shape (grade F)
    post_trade(day_id, {
        "sweep_confirmed": True, "pda_confirmed": True,
        "ifvg_confirmed": True, "vshape_confirmed": False,
    })

    # 6. FOMO (grade A — setup válido + followed_rules=True + clean_reaction=False)
    post_trade(day_id, {
        "sweep_confirmed": True, "pda_confirmed": True,
        "ifvg_confirmed": True, "vshape_confirmed": True,
        "followed_rules": True, "emotional_state": "fomo",
    })

    # 7. Ansiedad
    post_trade(day_id, {
        "sweep_confirmed": True, "pda_confirmed": True,
        "ifvg_confirmed": True, "vshape_confirmed": True,
        "emotional_state": "ansioso",
    })

    # 8. Frustración
    post_trade(day_id, {
        "sweep_confirmed": True, "pda_confirmed": True,
        "ifvg_confirmed": True, "vshape_confirmed": True,
        "emotional_state": "frustrado",
    })

    # 9. followed_rules=False (grade B)
    post_trade(day_id, {
        "sweep_confirmed": True, "pda_confirmed": True,
        "ifvg_confirmed": True, "vshape_confirmed": True,
        "followed_rules": False,
    })

    # 10. Salida por miedo
    post_trade(day_id, {
        "sweep_confirmed": True, "pda_confirmed": True,
        "ifvg_confirmed": True, "vshape_confirmed": True,
        "exit_reason": "por_miedo",
    })

    # 11. Salida por impulso
    post_trade(day_id, {
        "sweep_confirmed": True, "pda_confirmed": True,
        "ifvg_confirmed": True, "vshape_confirmed": True,
        "exit_reason": "por_impulso",
    })

    print("  11 trades creados\n")

    # ── GET /metrics ──────────────────────────────────────────────────────────
    r = requests.get(f"{BASE}/metrics")
    if not check("GET /metrics -> 200", r.status_code == 200, f"status={r.status_code}"):
        print(f"  Response: {r.text}")
        return
    m = r.json()

    # ── Métricas existentes presentes ────────────────────────────────────────
    legacy = [
        "total_trades", "valid_setups", "invalid_setups",
        "avg_result_r", "winrate_overall", "winrate_valid_setups",
    ]
    for key in legacy:
        check(f"métrica legacy '{key}' presente", key in m)

    # ── Nuevas métricas presentes y >= 1 ─────────────────────────────────────
    new_metrics = {
        "trades_without_sweep":       "trade sin sweep (#2)",
        "trades_without_pda":         "trade sin PDA (#3)",
        "trades_without_ifvg":        "trade sin IFVG (#4)",
        "trades_without_vshape":      "trade sin V-Shape (#5)",
        "trades_unclean_reaction":    "trades válidos sin clean_reaction",
        "trades_outside_ny_killzone": "trades válidos sin NY killzone",
        "fomo_trades":                "trade con FOMO (#6)",
        "anxiety_trades":             "trade con ansiedad (#7)",
        "frustration_trades":         "trade con frustración (#8)",
        "rule_break_trades":          "trade con followed_rules=false (#9)",
        "fear_exits":                 "trade con salida por miedo (#10)",
        "impulse_exits":              "trade con salida por impulso (#11)",
        "grade_a_plus_trades":        "grade A+ (#1)",
        "grade_a_trades":             "grade A (#6)",
        "grade_b_trades":             "grade B (#9)",
        "grade_c_trades":             "grade C (#2)",
        "grade_f_trades":             "grade F (#3,4,5)",
    }
    for key, desc in new_metrics.items():
        present = key in m
        check(f"'{key}' presente en /metrics", present)
        if present:
            check(f"'{key}' >= 1 ({desc})", m[key] >= 1, f"got={m[key]}")

    # ── Ninguna métrica es None ───────────────────────────────────────────────
    none_keys = [k for k, v in m.items() if v is None]
    check("ninguna métrica retorna None", len(none_keys) == 0, f"None en: {none_keys}")

    print()
    all_ok = all(results)
    print("RESULTADO FINAL:", "FASE 14C PASS" if all_ok else "FASE 14C FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    run()
