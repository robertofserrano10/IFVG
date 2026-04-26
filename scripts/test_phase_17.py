import sys
import requests

BASE = "http://127.0.0.1:8000"
results = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append(condition)
    print(f"[{status}] {label}" + (f" -- {detail}" if detail else ""))
    return condition


def make_trade(day_id, result_r, followed_rules=False, win=False):
    return {
        "trading_day_id":  day_id,
        "direction":       "long" if (result_r or 0) >= 0 else "short",
        "sweep_confirmed": True,
        "pda_confirmed":   True,
        "ifvg_confirmed":  True,
        "vshape_confirmed": True,
        "entry_price":     19800.0,
        "stop_loss":       19750.0,
        "take_profit":     19900.0,
        "result_r":        result_r,
        "followed_rules":  followed_rules,
    }


def run():
    print("=== Phase 17: Discipline Tracking ===\n")

    # Crear 3 días (overtrading_days > 2 requires >3 days with >2 trades)
    day_ids = []
    dates = ["2026-05-01", "2026-05-02", "2026-05-03"]
    for d in dates:
        r = requests.post(f"{BASE}/trading-days", json={
            "trade_date": d,
            "market": "NQ",
            "is_news_day": False,
            "is_ath_context": False,
        })
        if not check(f"POST /trading-days {d} -> 201", r.status_code == 201, f"status={r.status_code}"):
            print("Abortando.")
            return
        day_ids.append(r.json()["id"])

    # Dia 1: 3 trades todos pérdidas, sin reglas → overtrading + racha negativa + rule break
    # Dia 2: 3 trades todos pérdidas, sin reglas → overtrading + racha negativa continúa
    # Dia 3: 3 trades mezcla pero más pérdidas que ganancias, sin reglas → overtrading + baja disciplina

    trades_plan = [
        # day 0: 3 losses, rule breaks
        (0, -1.0, False),
        (0, -1.5, False),
        (0, -2.0, False),
        # day 1: 3 losses, rule breaks (streak now 6)
        (1, -1.0, False),
        (1, -1.5, False),
        (1, -0.5, False),
        # day 2: 3 trades, 1 win + 2 losses, rule breaks
        (2, 1.0,  False),
        (2, -1.0, False),
        (2, -1.5, False),
    ]

    created = 0
    for day_idx, result_r, followed_rules in trades_plan:
        r = requests.post(f"{BASE}/trades", json=make_trade(day_ids[day_idx], result_r, followed_rules))
        if r.status_code == 201:
            created += 1
    check("Todos los trades creados", created == len(trades_plan),
          f"{created}/{len(trades_plan)}")

    # GET /metrics
    r = requests.get(f"{BASE}/metrics")
    if not check("GET /metrics -> 200", r.status_code == 200, f"status={r.status_code}"):
        print(f"  {r.text[:300]}")
        return
    m = r.json()

    # Validar campos fase 17
    check("overtrading_days existe",   "overtrading_days"   in m)
    check("avg_trades_per_day existe", "avg_trades_per_day" in m)
    check("max_win_streak existe",     "max_win_streak"     in m)
    check("max_loss_streak existe",    "max_loss_streak"    in m)
    check("current_streak existe",     "current_streak"     in m)
    check("disciplined_ratio existe",  "disciplined_ratio"  in m)
    check("rule_break_rate existe",    "rule_break_rate"    in m)
    check("discipline_alerts existe",  "discipline_alerts"  in m)

    # Validar tipos
    if "overtrading_days" in m:
        check("overtrading_days es entero",   isinstance(m["overtrading_days"], int))
    if "avg_trades_per_day" in m:
        check("avg_trades_per_day es número", isinstance(m["avg_trades_per_day"], (int, float)))
    if "max_loss_streak" in m:
        check("max_loss_streak es entero",    isinstance(m["max_loss_streak"], int))
    if "current_streak" in m:
        check("current_streak es entero",     isinstance(m["current_streak"], int))
    if "disciplined_ratio" in m:
        check("disciplined_ratio es número",  isinstance(m["disciplined_ratio"], (int, float)))
    if "rule_break_rate" in m:
        check("rule_break_rate es número",    isinstance(m["rule_break_rate"], (int, float)))

    if "discipline_alerts" in m:
        alerts = m["discipline_alerts"]
        check("discipline_alerts es lista",   isinstance(alerts, list))
        check("alerts no vacío",              len(alerts) >= 1,
              f"alerts={alerts}")
        if alerts:
            check("alerts contiene strings",  all(isinstance(s, str) for s in alerts))

    # Validar valores lógicos (con los datos que creamos)
    if "overtrading_days" in m:
        check("overtrading_days >= 3",        m["overtrading_days"] >= 3,
              f"overtrading_days={m['overtrading_days']}")
    if "max_loss_streak" in m:
        check("max_loss_streak >= 3",         m["max_loss_streak"] >= 3,
              f"max_loss_streak={m['max_loss_streak']}")

    # Verificar que métricas existentes no se rompieron
    for k in ["total_trades", "winrate_overall", "performance_insights",
              "winrate_by_liquidity", "grade_a_plus_trades"]:
        check(f"métrica '{k}' intacta", k in m)

    print()
    all_ok = all(results)
    print("RESULTADO FINAL:", "FASE 17 PASS" if all_ok else "FASE 17 FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    run()
