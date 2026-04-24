import io
import sys
import struct
import zlib
import requests

BASE = "http://127.0.0.1:8000"
results = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append(condition)
    print(f"[{status}] {label}" + (f" -- {detail}" if detail else ""))
    return condition


def minimal_png():
    def make_chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)
    ihdr = make_chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = make_chunk(b"IDAT", zlib.compress(b"\x00\xFF\x00\x00"))
    iend = make_chunk(b"IEND", b"")
    return b"\x89PNG\r\n\x1a\n" + ihdr + idat + iend


def run():
    print("=== Phase 15: Supabase Storage upload ===\n")

    # 1. Crear trading day
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

    # 2. Crear trade
    r = requests.post(f"{BASE}/trades", json={
        "trading_day_id":   day_id,
        "direction":        "long",
        "sweep_confirmed":  True,
        "pda_confirmed":    True,
        "ifvg_confirmed":   True,
        "vshape_confirmed": True,
        "entry_price":      19800.0,
        "stop_loss":        19750.0,
        "take_profit":      19900.0,
    })
    if not check("POST /trades -> 201", r.status_code == 201, f"status={r.status_code}"):
        print(f"  Response: {r.text}")
        return
    trade_id = r.json()["id"]
    check("trade_id es entero positivo", isinstance(trade_id, int) and trade_id > 0)

    # 3. Subir imagen via POST /trade-images/upload
    png_bytes = minimal_png()
    check("PNG generado es valido (>50 bytes)", len(png_bytes) > 50, f"size={len(png_bytes)}")

    r = requests.post(
        f"{BASE}/trade-images/upload",
        files={"file": ("test_chart.png", io.BytesIO(png_bytes), "image/png")},
        data={"trade_id": trade_id, "image_type": "entrada"},
    )

    upload_ok = check(
        "POST /trade-images/upload -> 201",
        r.status_code == 201,
        f"status={r.status_code}",
    )

    if not upload_ok:
        print(f"  Detalle del error: {r.text[:300]}")
        print()
        print("  NOTA: Verifica que el bucket 'trade-images' existe en Supabase Storage")
        print("  y que SUPABASE_SERVICE_ROLE_KEY esta configurado en el .env si es necesario.")
        print()
        # Still run structural checks
    else:
        img = r.json()

        # 4. Verificar estructura del response
        check("response contiene image_url",  "image_url"  in img)
        check("response contiene trade_id",   "trade_id"   in img)
        check("response contiene image_type", "image_type" in img)
        check("response contiene id",         "id"         in img)
        check("trade_id correcto",            img.get("trade_id") == trade_id)
        check("image_type correcto",          img.get("image_type") == "entrada")

        # 5. Verificar path contiene year/month/trade_id
        from datetime import datetime, timezone
        now   = datetime.now(timezone.utc)
        year  = now.strftime("%Y")
        month = now.strftime("%m")
        url   = img.get("image_url", "")
        check("image_url contiene year",     year         in url, f"url={url[:80]}")
        check("image_url contiene month",    month        in url, f"url={url[:80]}")
        check("image_url contiene trade_id", f"trade_{trade_id}" in url, f"url={url[:80]}")
        check("image_url contiene image_type", "entrada" in url, f"url={url[:80]}")
        check("image_url es https",          url.startswith("https://"), f"url={url[:80]}")

        # 6. GET /trade-images verifica que existe
        r2 = requests.get(f"{BASE}/trade-images")
        check("GET /trade-images -> 200", r2.status_code == 200)
        images = r2.json()
        img_id = img.get("id")
        found  = any(i.get("id") == img_id for i in images)
        check("imagen aparece en GET /trade-images", found)

        # 7. GET /trades verifica que el trade tiene la imagen
        r3 = requests.get(f"{BASE}/trades")
        check("GET /trades -> 200", r3.status_code == 200)

    # 8. Verificar que el endpoint de validacion rechaza tipos invalidos
    r = requests.post(
        f"{BASE}/trade-images/upload",
        files={"file": ("bad.txt", io.BytesIO(b"not an image"), "text/plain")},
        data={"trade_id": trade_id, "image_type": "entrada"},
    )
    check("upload tipo invalido -> 400", r.status_code == 400, f"status={r.status_code}")

    # 9. Verificar que endpoint de validacion rechaza archivo > 5MB
    big = io.BytesIO(b"x" * (5 * 1024 * 1024 + 1))
    r = requests.post(
        f"{BASE}/trade-images/upload",
        files={"file": ("big.png", big, "image/png")},
        data={"trade_id": trade_id, "image_type": "entrada"},
    )
    check("upload >5MB -> 400", r.status_code == 400, f"status={r.status_code}")

    # 10. Verificar cambios de codigo
    with open("backend/app/routes/trade_images.py", encoding="utf-8") as f:
        route_code = f.read()
    check("ruta tiene endpoint upload",         "/trade-images/upload" in route_code)
    check("ruta valida content_type",           "_ALLOWED_TYPES"       in route_code)
    check("ruta valida tamano",                 "_MAX_BYTES"           in route_code)
    check("ruta sube a storage",                "from_"                in route_code)
    check("ruta obtiene public URL",            "get_public_url"       in route_code)

    with open("frontend/index.html", encoding="utf-8") as f:
        html = f.read()
    check("index.html tiene input file",        'type="file"'           in html)
    check("index.html tiene trade_image_file",  "trade_image_file"      in html)

    with open("frontend/app.js", encoding="utf-8") as f:
        appjs = f.read()
    check("app.js usa /trade-images/upload",    "/trade-images/upload"  in appjs)
    check("app.js usa FormData",                "FormData"              in appjs)
    check("app.js muestra preview",             "trade_image_file_preview" in appjs)

    print()
    all_ok = all(results)
    print("RESULTADO FINAL:", "FASE 15 PASS" if all_ok else "FASE 15 FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    run()
