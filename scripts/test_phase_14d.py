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
    print("=== Phase 14D: dashboard visual de errores y grades ===\n")

    # 1. GET /metrics funciona
    r = requests.get(f"{BASE}/metrics")
    if not check("GET /metrics -> 200", r.status_code == 200, f"status={r.status_code}"):
        print(f"  Response: {r.text}")
        return
    m = r.json()

    # 2. Metricas de errores tecnicos presentes
    tech_keys = [
        "trades_without_sweep", "trades_without_pda",
        "trades_without_ifvg", "trades_without_vshape",
        "trades_unclean_reaction", "trades_outside_ny_killzone",
    ]
    for key in tech_keys:
        check(f"metrica tecnica '{key}' presente", key in m, f"got={m.get(key)}")

    # 3. Metricas psicologicas presentes
    psych_keys = [
        "fomo_trades", "anxiety_trades", "frustration_trades",
        "rule_break_trades", "fear_exits", "impulse_exits",
    ]
    for key in psych_keys:
        check(f"metrica psicologica '{key}' presente", key in m, f"got={m.get(key)}")

    # 4. Metricas de grades presentes
    grade_keys = [
        "grade_a_plus_trades", "grade_a_trades",
        "grade_b_trades", "grade_c_trades", "grade_f_trades",
    ]
    for key in grade_keys:
        check(f"metrica de grade '{key}' presente", key in m, f"got={m.get(key)}")

    # 5. Ninguna metrica es None
    none_keys = [k for k, v in m.items() if v is None]
    check("ninguna metrica es None", len(none_keys) == 0, f"None en: {none_keys}")

    # 6. index.html tiene estructura del dashboard de metricas
    with open("frontend/index.html", encoding="utf-8") as f:
        html = f.read()
    check("index.html contiene metricsSummary", 'id="metricsSummary"' in html)
    check("index.html contiene Resumen del Journal", "Resumen del Journal" in html)

    # 7. app.js renderiza las secciones del dashboard
    with open("frontend/app.js", encoding="utf-8") as f:
        appjs = f.read()

    check("app.js muestra 'Errores tecnicos'",       "Errores t" in appjs)
    check("app.js muestra 'Errores psicologicos'",   "Errores ps" in appjs)
    check("app.js muestra 'Calidad de ejecucion'",   "Calidad de ejecuci" in appjs)
    check("app.js muestra 'Resumen general'",        "Resumen general" in appjs)

    # 8. app.js usa las nuevas metricas de grades
    for key in grade_keys:
        check(f"app.js usa m.{key}", f"m.{key}" in appjs)

    # 9. app.js usa las nuevas metricas tecnicas
    for key in tech_keys:
        check(f"app.js usa m.{key}", f"m.{key}" in appjs)

    # 10. app.js usa las nuevas metricas psicologicas nuevas
    new_psych = ["frustration_trades", "rule_break_trades"]
    for key in new_psych:
        check(f"app.js usa m.{key}", f"m.{key}" in appjs)

    # 11. CSS tiene grade-grid y grade-metric-card
    with open("frontend/styles.css", encoding="utf-8") as f:
        css = f.read()
    check("styles.css contiene .grade-grid",        ".grade-grid" in css)
    check("styles.css contiene .grade-metric-card", ".grade-metric-card" in css)
    check("styles.css contiene .metrics-section",   ".metrics-section" in css)
    check("styles.css contiene .grade-a-plus",      "grade-a-plus" in css)
    check("styles.css contiene .grade-f",           "grade-f" in css)

    print()
    all_ok = all(results)
    print("RESULTADO FINAL:", "FASE 14D PASS" if all_ok else "FASE 14D FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    run()
