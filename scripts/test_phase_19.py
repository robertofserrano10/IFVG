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
    print("=== Phase 19: UX Pro ===\n")

    # 1. API smoke test
    r = requests.get(f"{BASE}/trades")
    check("GET /trades -> 200", r.status_code == 200, f"status={r.status_code}")

    r2 = requests.get(f"{BASE}/trading-days")
    check("GET /trading-days -> 200", r2.status_code == 200, f"status={r2.status_code}")

    # 2. index.html checks
    with open("frontend/index.html", encoding="utf-8") as f:
        html = f.read()

    check("index.html tiene trade_search input", "trade_search" in html)
    check("index.html tiene applyTradeFilters en oninput", "applyTradeFilters" in html)
    check("index.html tiene filter_grade select", "filter_grade" in html)
    check("index.html tiene filter_killzone select", "filter_killzone" in html)
    check("index.html tiene opcion A+", "A+" in html)

    # 3. app.js checks
    with open("frontend/app.js", encoding="utf-8") as f:
        js = f.read()

    check("app.js tiene applyTradeFilters",        "applyTradeFilters"   in js)
    check("app.js filtra por trade_search",        "trade_search"        in js)
    check("app.js filtra por filter_grade",        "filter_grade"        in js)
    check("app.js filtra por filter_killzone",     "filter_killzone"     in js)
    check("app.js tiene renderTradeCard",          "renderTradeCard"     in js)
    check("app.js tiene day-group",                "day-group"           in js)
    check("app.js tiene highlight-aplus",          "highlight-aplus"     in js)
    check("app.js tiene highlight-error",          "highlight-error"     in js)
    check("app.js tiene highlight-psychology",     "highlight-psychology" in js)
    check("app.js tiene trade-positive",           "trade-positive"      in js)
    check("app.js tiene trade-negative",           "trade-negative"      in js)
    check("app.js tiene trade-be",                 "trade-be"            in js)

    # 4. styles.css checks
    with open("frontend/styles.css", encoding="utf-8") as f:
        css = f.read()

    check("styles.css tiene .positive",            ".positive"           in css)
    check("styles.css tiene .negative",            ".negative"           in css)
    check("styles.css tiene .trade-positive",      ".trade-positive"     in css)
    check("styles.css tiene .trade-negative",      ".trade-negative"     in css)
    check("styles.css tiene .trade-be",            ".trade-be"           in css)
    check("styles.css tiene .highlight-error",     ".highlight-error"    in css)
    check("styles.css tiene .highlight-psychology",".highlight-psychology" in css)
    check("styles.css tiene .highlight-aplus",     ".highlight-aplus"    in css)
    check("styles.css tiene .day-group",           ".day-group"          in css)
    check("styles.css tiene .day-group-header",    ".day-group-header"   in css)
    check("styles.css tiene .day-summary",         ".day-summary"        in css)
    check("styles.css tiene #trade_search",        "#trade_search"       in css)
    check("styles.css tiene .search-wrapper",      ".search-wrapper"     in css)

    print()
    all_ok = all(results)
    print("RESULTADO FINAL:", "FASE 19 PASS" if all_ok else "FASE 19 FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    run()
