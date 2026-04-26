import io
import subprocess
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
    print("=== Phase 20: Final Hardening ===\n")

    # ── Core endpoints ──────────────────────────────────────────────────────────
    r = requests.get(f"{BASE}/health")
    check("GET /health -> 200", r.status_code == 200, f"status={r.status_code}")

    r = requests.get(f"{BASE}/metrics")
    check("GET /metrics -> 200", r.status_code == 200, f"status={r.status_code}")

    r = requests.get(f"{BASE}/trades")
    check("GET /trades -> 200", r.status_code == 200, f"status={r.status_code}")

    # ── PDF year/month validation ───────────────────────────────────────────────
    r = requests.get(f"{BASE}/reports/monthly/pdf?year=1800&month=1")
    check("GET /reports/monthly/pdf year=1800 -> 400", r.status_code == 400,
          f"status={r.status_code}")

    r = requests.get(f"{BASE}/reports/monthly/pdf?year=2026&month=0")
    check("GET /reports/monthly/pdf month=0 -> 400", r.status_code == 400,
          f"status={r.status_code}")

    r = requests.get(f"{BASE}/reports/monthly/pdf?year=2026&month=13")
    check("GET /reports/monthly/pdf month=13 -> 400", r.status_code == 400,
          f"status={r.status_code}")

    r = requests.get(f"{BASE}/reports/monthly/pdf?year=2200&month=1")
    check("GET /reports/monthly/pdf year=2200 -> 400", r.status_code == 400,
          f"status={r.status_code}")

    r = requests.get(f"{BASE}/reports/monthly/pdf?year=2026&month=5")
    check("GET /reports/monthly/pdf year=2026 month=5 -> 200", r.status_code == 200,
          f"status={r.status_code}")

    # ── image_type validation ──────────────────────────────────────────────────
    minimal_png = (
        b'\x89PNG\r\n\x1a\n'
        b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx'
        b'\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
        b'\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    r = requests.post(
        f"{BASE}/trade-images/upload",
        data={"trade_id": "999", "image_type": "invalido"},
        files={"file": ("test.png", io.BytesIO(minimal_png), "image/png")},
    )
    check("POST /trade-images/upload image_type=invalido -> 400", r.status_code == 400,
          f"status={r.status_code}")

    r = requests.post(
        f"{BASE}/trade-images/upload",
        data={"trade_id": "999", "image_type": "captura"},
        files={"file": ("test.png", io.BytesIO(minimal_png), "image/png")},
    )
    check("POST /trade-images/upload image_type=captura -> 400", r.status_code == 400,
          f"status={r.status_code}")

    # ── .gitignore ─────────────────────────────────────────────────────────────
    with open(".gitignore", encoding="utf-8") as f:
        gi = f.read()
    check(".gitignore contiene .env",          ".env"         in gi)
    check(".gitignore contiene .venv/",         ".venv/"       in gi)
    check(".gitignore contiene __pycache__/",   "__pycache__/" in gi)
    check(".gitignore contiene *.pyc",          "*.pyc"        in gi)

    # ── backend/.env NOT git-tracked ────────────────────────────────────────────
    proc = subprocess.run(
        ["git", "ls-files", "backend/.env"],
        capture_output=True, text=True,
    )
    check("backend/.env no está en git tracking",
          proc.stdout.strip() == "",
          f"git output: '{proc.stdout.strip()}'")

    # ── requirements.txt ───────────────────────────────────────────────────────
    with open("backend/requirements.txt", encoding="utf-8") as f:
        req = f.read()
    check("requirements.txt contiene fastapi",          "fastapi"          in req)
    check("requirements.txt contiene uvicorn",          "uvicorn"          in req)
    check("requirements.txt contiene supabase",         "supabase"         in req)
    check("requirements.txt contiene python-dotenv",    "python-dotenv"    in req)
    check("requirements.txt contiene python-multipart", "python-multipart" in req)
    check("requirements.txt contiene fpdf2",            "fpdf2"            in req)

    # ── Frontend error handling ─────────────────────────────────────────────────
    with open("frontend/app.js", encoding="utf-8") as f:
        js = f.read()
    check("app.js valida campos obligatorios en saveTradingDay", "obligatori"      in js)
    check("app.js valida trading_day_id en saveTrade",           "Debes seleccionar" in js)
    check("app.js maneja error en loadMetrics",                  "catch" in js and "loadMetrics" in js)
    check("app.js maneja error en downloadMonthlyPDF",           "catch" in js and "downloadMonthlyPDF" in js)
    check("app.js valida rango de año en PDF",                   "2000" in js and "2100" in js)

    # ── Backend no expone secrets ───────────────────────────────────────────────
    health_text = requests.get(f"{BASE}/health").text
    check("GET /health no expone SUPABASE_SERVICE_ROLE_KEY",
          "SUPABASE_SERVICE_ROLE_KEY" not in health_text)

    metrics_text = requests.get(f"{BASE}/metrics").text
    check("GET /metrics no expone SUPABASE_SERVICE_ROLE_KEY",
          "SUPABASE_SERVICE_ROLE_KEY" not in metrics_text)

    # ── Backend source validation checks ───────────────────────────────────────
    with open("backend/app/routes/reports.py", encoding="utf-8") as f:
        rpt = f.read()
    check("reports.py valida year con 400",  "status_code=400" in rpt and "year" in rpt)
    check("reports.py valida month con 400", "status_code=400" in rpt and "month" in rpt)
    check("reports.py usa _safe_err",        "_safe_err" in rpt)

    with open("backend/app/routes/trade_images.py", encoding="utf-8") as f:
        img = f.read()
    check("trade_images.py define _ALLOWED_IMAGE_TYPES", "_ALLOWED_IMAGE_TYPES" in img)
    check("trade_images.py valida image_type con 400",   "status_code=400" in img and "image_type" in img)
    check("trade_images.py usa _safe_err",               "_safe_err" in img)

    print()
    all_ok = all(results)
    print("RESULTADO FINAL:", "FASE 20 PASS" if all_ok else "FASE 20 FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    run()
