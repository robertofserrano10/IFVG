import sys
import requests

BASE = "http://127.0.0.1:8000"
results = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append(condition)
    print(f"[{status}] {label}" + (f" -- {detail}" if detail else ""))
    return condition


def run():
    print("=== Phase 16: Performance Analysis ===\n")

    # 1. Crear trading day
    r = requests.post(f"{BASE}/trading-days", json={
        "trade_date": "2026-04-25",
        "market": "NQ",
        "is_news_day": False,
        "is_ath_context": False,
    })
    if not check("POST /trading-days -> 201", r.status_code == 201, f"status={r.status_code}"):
        print("Abortando.")
        return
    day_id = r.json()["id"]

    # 2. Crear trades con variedad de atributos
    trades_data = [
        # ny_killzone=True, clean_reaction=True → wins
        {"trading_day_id": day_id, "direction": "long",
         "sweep_confirmed": True, "pda_confirmed": True, "ifvg_confirmed": True, "vshape_confirmed": True,
         "entry_price": 19800.0, "stop_loss": 19750.0, "take_profit": 19900.0,
         "ny_killzone": True, "clean_reaction": True, "liquidity_type": "ny_am",
         "result_r": 2.0, "followed_rules": True},
        {"trading_day_id": day_id, "direction": "long",
         "sweep_confirmed": True, "pda_confirmed": True, "ifvg_confirmed": True, "vshape_confirmed": True,
         "entry_price": 19800.0, "stop_loss": 19750.0, "take_profit": 19900.0,
         "ny_killzone": True, "clean_reaction": True, "liquidity_type": "ny_am",
         "result_r": 1.5, "followed_rules": True},
        {"trading_day_id": day_id, "direction": "long",
         "sweep_confirmed": True, "pda_confirmed": True, "ifvg_confirmed": True, "vshape_confirmed": True,
         "entry_price": 19800.0, "stop_loss": 19750.0, "take_profit": 19900.0,
         "ny_killzone": True, "clean_reaction": True, "liquidity_type": "pdh",
         "result_r": 1.0, "followed_rules": True},
        # ny_killzone=False, clean_reaction=False, FOMO → losses
        {"trading_day_id": day_id, "direction": "short",
         "sweep_confirmed": True, "pda_confirmed": True, "ifvg_confirmed": True, "vshape_confirmed": True,
         "entry_price": 19800.0, "stop_loss": 19850.0, "take_profit": 19700.0,
         "ny_killzone": False, "clean_reaction": False, "liquidity_type": "london",
         "result_r": -1.0, "followed_rules": False, "emotional_state": "fomo"},
        {"trading_day_id": day_id, "direction": "short",
         "sweep_confirmed": True, "pda_confirmed": True, "ifvg_confirmed": True, "vshape_confirmed": True,
         "entry_price": 19800.0, "stop_loss": 19850.0, "take_profit": 19700.0,
         "ny_killzone": False, "clean_reaction": False, "liquidity_type": "london",
         "result_r": -1.5, "followed_rules": False, "emotional_state": "fomo"},
        # ny_killzone=False, clean_reaction=False, ansiedad → losses
        {"trading_day_id": day_id, "direction": "short",
         "sweep_confirmed": True, "pda_confirmed": True, "ifvg_confirmed": True, "vshape_confirmed": True,
         "entry_price": 19800.0, "stop_loss": 19850.0, "take_profit": 19700.0,
         "ny_killzone": False, "clean_reaction": False, "liquidity_type": "asia",
         "result_r": -1.0, "followed_rules": False, "emotional_state": "ansioso"},
        {"trading_day_id": day_id, "direction": "short",
         "sweep_confirmed": True, "pda_confirmed": True, "ifvg_confirmed": True, "vshape_confirmed": True,
         "entry_price": 19800.0, "stop_loss": 19850.0, "take_profit": 19700.0,
         "ny_killzone": False, "clean_reaction": False, "liquidity_type": "asia",
         "result_r": -2.0, "followed_rules": False, "emotional_state": "ansioso"},
        # frustración → losses
        {"trading_day_id": day_id, "direction": "short",
         "sweep_confirmed": True, "pda_confirmed": True, "ifvg_confirmed": True, "vshape_confirmed": True,
         "entry_price": 19800.0, "stop_loss": 19850.0, "take_profit": 19700.0,
         "ny_killzone": False, "clean_reaction": False, "liquidity_type": "ndog",
         "result_r": -1.0, "followed_rules": False, "emotional_state": "frustrado"},
        {"trading_day_id": day_id, "direction": "short",
         "sweep_confirmed": True, "pda_confirmed": True, "ifvg_confirmed": True, "vshape_confirmed": True,
         "entry_price": 19800.0, "stop_loss": 19850.0, "take_profit": 19700.0,
         "ny_killzone": False, "clean_reaction": False, "liquidity_type": "nwog",
         "result_r": -1.5, "followed_rules": False, "emotional_state": "frustrado"},
    ]

    trade_ids = []
    for td in trades_data:
        r = requests.post(f"{BASE}/trades", json=td)
        if r.status_code == 201:
            trade_ids.append(r.json()["id"])
    check("Trades creados correctamente", len(trade_ids) == len(trades_data),
          f"{len(trade_ids)}/{len(trades_data)} creados")

    # 3. GET /metrics
    r = requests.get(f"{BASE}/metrics")
    if not check("GET /metrics -> 200", r.status_code == 200, f"status={r.status_code}"):
        print(f"  Response: {r.text[:300]}")
        return
    m = r.json()

    # 4. Validar campos requeridos
    check("winrate_by_liquidity existe",       "winrate_by_liquidity"        in m)
    check("winrate_ny_killzone existe",        "winrate_ny_killzone"         in m)
    check("winrate_outside_ny_killzone existe","winrate_outside_ny_killzone" in m)
    check("winrate_clean_reaction existe",     "winrate_clean_reaction"      in m)
    check("winrate_unclean_reaction existe",   "winrate_unclean_reaction"    in m)
    check("winrate_fomo existe",               "winrate_fomo"                in m)
    check("winrate_ansiedad existe",           "winrate_ansiedad"            in m)
    check("winrate_frustracion existe",        "winrate_frustracion"         in m)
    check("performance_insights existe",       "performance_insights"        in m)

    # 5. Validar tipos
    if "winrate_by_liquidity" in m:
        check("winrate_by_liquidity es dict",  isinstance(m["winrate_by_liquidity"], dict))
        liq = m["winrate_by_liquidity"]
        for lt in ["asia", "london", "pdh", "pdl", "nwog", "ndog", "ny_am", "other"]:
            check(f"winrate_by_liquidity contiene '{lt}'", lt in liq)

    if "winrate_ny_killzone" in m:
        check("winrate_ny_killzone es numero", isinstance(m["winrate_ny_killzone"], (int, float)))
    if "winrate_clean_reaction" in m:
        check("winrate_clean_reaction es numero", isinstance(m["winrate_clean_reaction"], (int, float)))
    if "winrate_fomo" in m:
        check("winrate_fomo es numero", isinstance(m["winrate_fomo"], (int, float)))

    if "performance_insights" in m:
        insights = m["performance_insights"]
        check("performance_insights es lista",  isinstance(insights, list))
        check("insights no vacío",             len(insights) >= 1,
              f"insights={insights}")
        if insights:
            check("insights contiene strings",  all(isinstance(s, str) for s in insights))

    # 6. Validar que métricas existentes no se rompieron
    existing_keys = [
        "total_trades", "valid_setups", "invalid_setups",
        "winrate_overall", "winrate_valid_setups", "avg_result_r",
        "grade_a_plus_trades", "grade_a_trades", "grade_b_trades",
        "fomo_trades", "anxiety_trades", "frustration_trades",
    ]
    for k in existing_keys:
        check(f"métrica existente '{k}' intacta", k in m)

    print()
    all_ok = all(results)
    print("RESULTADO FINAL:", "FASE 16 PASS" if all_ok else "FASE 16 FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    run()
