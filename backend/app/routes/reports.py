import re
from collections import defaultdict

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from fpdf import FPDF

from app.database import get_supabase_client


def _safe_err(e: Exception) -> str:
    return re.sub(r'eyJ[A-Za-z0-9\-_]{10,}', '[REDACTED]', str(e))

router = APIRouter()

_MONTH_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


def _winrate(rl):
    if not rl:
        return 0.0
    return round(sum(1 for v in rl if v > 0) / len(rl) * 100, 1)


def _avg(vals):
    vs = [v for v in vals if v is not None]
    return round(sum(vs) / len(vs), 2) if vs else 0.0


def _grade(t):
    sv, fr, cr, nyk = (
        t.get("setup_valid", False), t.get("followed_rules"),
        t.get("clean_reaction", False), t.get("ny_killzone", False),
    )
    if sv and fr is True and cr and nyk:
        return "A+"
    if sv and fr is True:
        return "A"
    if sv and fr is False:
        return "B"
    if not sv and fr is True:
        return "C"
    return "F"


class _PDF(FPDF):
    def section(self, title):
        self.ln(3)
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(40, 40, 40)
        self.set_text_color(255, 255, 255)
        self.cell(self.epw, 6, f"  {title}", border=0, fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def kv(self, label, value):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 9)
        self.cell(125, 5, label, border=0, new_x="RIGHT", new_y="TOP")
        self.set_font("Helvetica", "B", 9)
        self.cell(self.epw - 125, 5, str(value), border=0, align="R",
                  new_x="LMARGIN", new_y="NEXT")

    def bullet(self, text):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 9)
        self.cell(6, 5, "-", new_x="RIGHT", new_y="TOP")
        self.multi_cell(self.epw - 6, 5, str(text)[:100],
                        new_x="LMARGIN", new_y="NEXT")


@router.get("/reports/monthly/pdf")
def get_monthly_pdf(year: int, month: int):
    if not (2000 <= year <= 2100):
        raise HTTPException(status_code=400, detail="Año inválido. Debe estar entre 2000 y 2100.")
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Mes inválido. Debe estar entre 1 y 12.")
    try:
        client = get_supabase_client()

        all_days   = client.table("trading_days").select("*").execute().data
        all_trades = client.table("trades").select("*").execute().data

        prefix     = f"{year:04d}-{month:02d}"
        month_days = [d for d in all_days if str(d.get("trade_date", "")).startswith(prefix)]
        day_ids    = {d["id"] for d in month_days}
        day_map    = {d["id"]: d for d in month_days}
        trades     = [t for t in all_trades if t.get("trading_day_id") in day_ids]

        valid   = [t for t in trades if t.get("setup_valid")]
        all_r   = [t["result_r"] for t in trades if t.get("result_r") is not None]
        total   = len(trades)

        wo_sweep  = sum(1 for t in trades if not t.get("sweep_confirmed",  False))
        wo_pda    = sum(1 for t in trades if not t.get("pda_confirmed",    False))
        wo_ifvg   = sum(1 for t in trades if not t.get("ifvg_confirmed",   False))
        wo_vshape = sum(1 for t in trades if not t.get("vshape_confirmed", False))
        uncl_cr   = sum(1 for t in trades if t.get("setup_valid") and not t.get("clean_reaction", False))
        out_nyk   = sum(1 for t in trades if t.get("setup_valid") and not t.get("ny_killzone",    False))

        fomo_cnt  = sum(1 for t in trades if t.get("emotional_state") == "fomo")
        anx_cnt   = sum(1 for t in trades if t.get("emotional_state") == "ansioso")
        frus_cnt  = sum(1 for t in trades if t.get("emotional_state") == "frustrado")
        rb_cnt    = sum(1 for t in trades if t.get("followed_rules") is False)
        fear_cnt  = sum(1 for t in trades if t.get("exit_reason") == "por_miedo")
        imp_cnt   = sum(1 for t in trades if t.get("exit_reason") == "por_impulso")

        grades = {g: sum(1 for t in trades if _grade(t) == g) for g in ("A+", "A", "B", "C", "F")}

        day_counts = defaultdict(int)
        for t in trades:
            if t.get("trading_day_id") is not None:
                day_counts[t["trading_day_id"]] += 1
        overtrading_days = sum(1 for c in day_counts.values() if c > 2)
        avg_tpd          = round(total / len(day_counts), 2) if day_counts else 0.0

        sorted_r = [t["result_r"] for t in sorted(
            [t for t in trades if t.get("result_r") is not None],
            key=lambda x: x.get("created_at", ""),
        )]
        max_ws = max_ls = cw = cl = 0
        for r in sorted_r:
            if r > 0:
                cw += 1; cl = 0; max_ws = max(max_ws, cw)
            elif r < 0:
                cl += 1; cw = 0; max_ls = max(max_ls, cl)
            else:
                cw = cl = 0

        disc_cnt   = sum(1 for t in trades if t.get("setup_valid") and t.get("followed_rules") is True)
        disc_ratio = round(disc_cnt / total, 2) if total else 0.0
        rb_rate    = round(rb_cnt   / total, 2) if total else 0.0

        nyk_r    = [t["result_r"] for t in trades if     t.get("ny_killzone")     and t.get("result_r") is not None]
        no_nyk_r = [t["result_r"] for t in trades if not t.get("ny_killzone")     and t.get("result_r") is not None]
        cr_r     = [t["result_r"] for t in trades if     t.get("clean_reaction")  and t.get("result_r") is not None]
        no_cr_r  = [t["result_r"] for t in trades if not t.get("clean_reaction")  and t.get("result_r") is not None]
        fomo_r   = [t["result_r"] for t in trades if t.get("emotional_state") == "fomo" and t.get("result_r") is not None]
        overall  = _winrate(all_r)

        insights = []
        if len(nyk_r) >= 2 and len(no_nyk_r) >= 2:
            d = _winrate(nyk_r) - _winrate(no_nyk_r)
            if abs(d) > 10:
                insights.append("Tu winrate es mayor en NY Killzone" if d > 0 else "Tu winrate es menor en NY Killzone")
        if len(cr_r) >= 2 and len(no_cr_r) >= 2:
            d = _winrate(cr_r) - _winrate(no_cr_r)
            if abs(d) > 10:
                insights.append("Tus resultados mejoran con clean reaction" if d > 0 else "Pierdes mas cuando no hay clean reaction")
        if len(fomo_r) >= 2 and all_r:
            d = _winrate(fomo_r) - overall
            if abs(d) > 10:
                insights.append("FOMO reduce tu winrate" if d < 0 else "FOMO no afecta negativamente tu winrate")
        if not insights:
            insights.append("No hay suficientes datos para generar insights")

        alerts = []
        if overtrading_days > 2:  alerts.append("Estas sobreoperando")
        if rb_rate > 0.3:         alerts.append("Estas rompiendo tus reglas frecuentemente")
        if max_ls >= 3:           alerts.append("Estas en racha negativa")
        if disc_ratio < 0.5:      alerts.append("Baja disciplina detectada")
        if not alerts:            alerts.append("Disciplina estable")

        # ── build PDF ──────────────────────────────────────────────────────────
        pdf = _PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(pdf.epw, 10, "REPORTE MENSUAL - TRADING JOURNAL", align="C",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(pdf.epw, 7, f"{_MONTH_ES.get(month, str(month))} {year}", align="C",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        pdf.section("RESUMEN GENERAL")
        pdf.kv("Total de trades",       total)
        pdf.kv("Setups validos",        len(valid))
        pdf.kv("Setups invalidos",      total - len(valid))
        pdf.kv("Winrate general",       f"{_winrate(all_r)}%")
        pdf.kv("Promedio R",            _avg(all_r))

        pdf.section("ERRORES TECNICOS")
        pdf.kv("Sin sweep",             wo_sweep)
        pdf.kv("Sin PDA HTF",           wo_pda)
        pdf.kv("Sin IFVG",              wo_ifvg)
        pdf.kv("Sin V-Shape",           wo_vshape)
        pdf.kv("Reaccion no limpia",    uncl_cr)
        pdf.kv("Fuera de KZ NY",        out_nyk)

        pdf.section("PSICOLOGIA")
        pdf.kv("FOMO",                  fomo_cnt)
        pdf.kv("Ansiedad",              anx_cnt)
        pdf.kv("Frustracion",           frus_cnt)
        pdf.kv("Rompio reglas",         rb_cnt)
        pdf.kv("Salida por miedo",      fear_cnt)
        pdf.kv("Salida por impulso",    imp_cnt)

        pdf.section("CALIDAD")
        for g in ("A+", "A", "B", "C", "F"):
            pdf.kv(f"Grade {g}",        grades[g])

        pdf.section("DISCIPLINA")
        pdf.kv("Dias sobreoperados",    overtrading_days)
        pdf.kv("Trades por dia (prom)", avg_tpd)
        pdf.kv("Racha ganadora max",    max_ws)
        pdf.kv("Racha perdedora max",   max_ls)
        pdf.kv("Ratio disciplina",      disc_ratio)
        pdf.kv("Tasa ruptura reglas",   rb_rate)

        pdf.section("INSIGHTS")
        for ins in insights:
            pdf.bullet(ins)

        pdf.section("ALERTAS DE DISCIPLINA")
        for a in alerts:
            pdf.bullet(a)

        pdf.section("TRADES DEL MES")
        if not trades:
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(pdf.epw, 5, "No hay trades registrados para este periodo.",
                     new_x="LMARGIN", new_y="NEXT")
        else:
            cols = [("Fecha", 30), ("Mercado", 20), ("Dir", 16),
                    ("Liquidez", 26), ("Valid", 14), ("R", 20), ("Grade", 14)]
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_fill_color(220, 220, 220)
            pdf.set_x(pdf.l_margin)
            for i, (lbl, w) in enumerate(cols):
                nx = "RIGHT" if i < len(cols) - 1 else "LMARGIN"
                ny = "TOP"   if i < len(cols) - 1 else "NEXT"
                pdf.cell(w, 5, lbl, border=1, fill=True, align="C",
                         new_x=nx, new_y=ny)
            pdf.set_font("Helvetica", "", 8)
            for t in trades[:30]:
                d        = day_map.get(t.get("trading_day_id"), {})
                fecha    = str(d.get("trade_date", ""))[:10]
                mercado  = str(d.get("market", ""))[:8]
                direc    = str(t.get("direction", ""))[:5]
                liq      = str(t.get("liquidity_type") or "")[:10]
                valid_l  = "Si" if t.get("setup_valid") else "No"
                r_val    = str(t.get("result_r")) if t.get("result_r") is not None else "-"
                grade    = _grade(t)
                row_data = [(fecha,30),(mercado,20),(direc,16),(liq,26),(valid_l,14),(r_val,20),(grade,14)]
                pdf.set_x(pdf.l_margin)
                for i, (val, w) in enumerate(row_data):
                    nx = "RIGHT" if i < len(row_data) - 1 else "LMARGIN"
                    ny = "TOP"   if i < len(row_data) - 1 else "NEXT"
                    pdf.cell(w, 5, val, border=1, align="C", new_x=nx, new_y=ny)

        pdf_bytes = bytes(pdf.output())
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="reporte_{year}_{month:02d}.pdf"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=_safe_err(e))
