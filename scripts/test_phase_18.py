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
    print("=== Phase 18: Monthly PDF Report ===\n")

    # 1. Crear trading day del mes
    r = requests.post(f"{BASE}/trading-days", json={
        "trade_date": "2026-05-20",
        "market": "NQ",
        "is_news_day": False,
        "is_ath_context": False,
    })
    if not check("POST /trading-days -> 201", r.status_code == 201, f"status={r.status_code}"):
        print("Abortando.")
        return
    day_id = r.json()["id"]

    # 2. Crear trades
    for result_r, followed in [(2.0, True), (-1.0, False), (1.5, True)]:
        r = requests.post(f"{BASE}/trades", json={
            "trading_day_id":  day_id,
            "direction":       "long",
            "sweep_confirmed": True,
            "pda_confirmed":   True,
            "ifvg_confirmed":  True,
            "vshape_confirmed": True,
            "entry_price":     19800.0,
            "stop_loss":       19750.0,
            "take_profit":     19900.0,
            "result_r":        result_r,
            "followed_rules":  followed,
            "liquidity_type":  "ny_am",
        })
        check(f"POST /trades (result_r={result_r}) -> 201", r.status_code == 201,
              f"status={r.status_code}")

    # 3. GET /reports/monthly/pdf
    r = requests.get(f"{BASE}/reports/monthly/pdf?year=2026&month=5")
    check("GET /reports/monthly/pdf -> 200", r.status_code == 200,
          f"status={r.status_code}" + (f" body={r.text[:200]}" if r.status_code != 200 else ""))

    # 4. Content-Type es application/pdf
    ct = r.headers.get("Content-Type", "")
    check("Content-Type es application/pdf", "application/pdf" in ct, f"Content-Type={ct}")

    # 5. PDF comienza con %PDF
    if r.status_code == 200:
        check("Respuesta comienza con %PDF", r.content[:4] == b"%PDF",
              f"primeros 4 bytes={r.content[:4]}")
        check("PDF tiene contenido (>1 KB)", len(r.content) > 1000,
              f"tamano={len(r.content)} bytes")
        check("Content-Disposition contiene reporte_", "reporte_" in r.headers.get("Content-Disposition", ""))

    # 6. Verificar endpoint sin datos del mes (mes diferente)
    r2 = requests.get(f"{BASE}/reports/monthly/pdf?year=2020&month=1")
    check("GET /reports/monthly/pdf mes vacio -> 200", r2.status_code == 200,
          f"status={r2.status_code}")
    if r2.status_code == 200:
        check("PDF vacio comienza con %PDF", r2.content[:4] == b"%PDF")

    # 7. Verificar frontend
    with open("frontend/index.html", encoding="utf-8") as f:
        html = f.read()
    check("index.html tiene texto 'Descargar reporte PDF mensual'",
          "Descargar reporte PDF mensual" in html)
    check("index.html tiene input pdf_year",     "pdf_year"  in html)
    check("index.html tiene select pdf_month",   "pdf_month" in html)
    check("index.html llama downloadMonthlyPDF", "downloadMonthlyPDF" in html)

    with open("frontend/app.js", encoding="utf-8") as f:
        js = f.read()
    check("app.js tiene downloadMonthlyPDF",     "downloadMonthlyPDF"   in js)
    check("app.js llama /reports/monthly/pdf",   "/reports/monthly/pdf" in js)

    # 8. Verificar backend
    with open("backend/app/routes/reports.py", encoding="utf-8") as f:
        rcode = f.read()
    check("reports.py tiene endpoint",           "/reports/monthly/pdf" in rcode)
    check("reports.py usa FPDF",                 "FPDF"                 in rcode)

    with open("backend/app/main.py", encoding="utf-8") as f:
        main = f.read()
    check("main.py importa reports_router",      "reports_router"       in main)
    check("main.py registra reports_router",     "include_router(reports_router)" in main)

    with open("backend/requirements.txt", encoding="utf-8") as f:
        req = f.read()
    check("requirements.txt tiene fpdf2",        "fpdf2" in req)

    print()
    all_ok = all(results)
    print("RESULTADO FINAL:", "FASE 18 PASS" if all_ok else "FASE 18 FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    run()
