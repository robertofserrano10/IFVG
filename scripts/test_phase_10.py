import requests

BASE = "http://127.0.0.1:8000"

EXPECTED_KEYS = [
    "total_trades", "valid_setups", "invalid_setups",
    "disciplined_trades", "discipline_errors",
    "fomo_trades", "anxiety_trades",
    "fear_exits", "impulse_exits",
    "avg_result_r", "avg_result_r_valid_setups",
    "winrate_overall", "winrate_valid_setups",
]


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" - {detail}" if detail else ""))
    return condition


def run():
    print("=== Phase 10: /metrics endpoint ===\n")

    r = requests.get(f"{BASE}/metrics")
    check("GET /metrics -> 200", r.status_code == 200, f"status={r.status_code}")
    if r.status_code != 200:
        print("Abortando.")
        return

    m = r.json()

    for key in EXPECTED_KEYS:
        check(f"clave '{key}' presente", key in m)

    check(
        "valid_setups + invalid_setups = total_trades",
        m["valid_setups"] + m["invalid_setups"] == m["total_trades"],
        f"{m['valid_setups']} + {m['invalid_setups']} != {m['total_trades']}",
    )
    check(
        "disciplined_trades <= valid_setups",
        m["disciplined_trades"] <= m["valid_setups"],
        f"{m['disciplined_trades']} > {m['valid_setups']}",
    )
    check(
        "discipline_errors <= valid_setups",
        m["discipline_errors"] <= m["valid_setups"],
        f"{m['discipline_errors']} > {m['valid_setups']}",
    )
    check(
        "fomo_trades <= total_trades",
        m["fomo_trades"] <= m["total_trades"],
    )
    check(
        "fear_exits + impulse_exits <= total_trades",
        m["fear_exits"] + m["impulse_exits"] <= m["total_trades"],
    )

    if m["avg_result_r"] is not None:
        check("avg_result_r es numerico", isinstance(m["avg_result_r"], (int, float)), f"tipo={type(m['avg_result_r'])}")

    if m["winrate_overall"] is not None:
        check("winrate_overall entre 0 y 100", 0 <= m["winrate_overall"] <= 100, f"got={m['winrate_overall']}")

    if m["winrate_valid_setups"] is not None:
        check("winrate_valid_setups entre 0 y 100", 0 <= m["winrate_valid_setups"] <= 100, f"got={m['winrate_valid_setups']}")

    print("\nMetricas actuales:")
    for k, v in m.items():
        print(f"  {k}: {v}")

    print("\nDone.")


if __name__ == "__main__":
    run()
