import requests

BASE = "http://127.0.0.1:8000"

NEVER_NONE = [
    "avg_result_r",
    "avg_result_r_valid_setups",
    "winrate_overall",
    "winrate_valid_setups",
]

ALL_KEYS = [
    "total_trades", "valid_setups", "invalid_setups",
    "disciplined_trades", "discipline_errors",
    "fomo_trades", "anxiety_trades",
    "fear_exits", "impulse_exits",
] + NEVER_NONE


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" - {detail}" if detail else ""))
    return condition


def run():
    print("=== Phase 11: metrics hardening (no None) ===\n")

    r = requests.get(f"{BASE}/metrics")
    check("GET /metrics -> 200", r.status_code == 200, f"status={r.status_code}")
    if r.status_code != 200:
        print("Abortando.")
        return

    m = r.json()

    for key in ALL_KEYS:
        check(f"clave '{key}' presente", key in m)

    for key in NEVER_NONE:
        v = m.get(key)
        check(f"{key} no es None", v is not None, f"got={v}")
        check(f"{key} es numerico", isinstance(v, (int, float)), f"tipo={type(v)}")

    if m.get("winrate_overall") is not None:
        check("winrate_overall entre 0 y 100", 0 <= m["winrate_overall"] <= 100, f"got={m['winrate_overall']}")
    if m.get("winrate_valid_setups") is not None:
        check("winrate_valid_setups entre 0 y 100", 0 <= m["winrate_valid_setups"] <= 100, f"got={m['winrate_valid_setups']}")

    check(
        "valid_setups + invalid_setups = total_trades",
        m["valid_setups"] + m["invalid_setups"] == m["total_trades"],
    )

    print("\nMetricas actuales:")
    for k, v in m.items():
        print(f"  {k}: {v}")

    print("\nDone.")


if __name__ == "__main__":
    run()
