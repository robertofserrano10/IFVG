from collections import defaultdict

from fastapi import APIRouter, HTTPException

from app.database import get_supabase_client

router = APIRouter()


def _safe_avg(values):
    vals = [v for v in values if v is not None]
    return round(sum(vals) / len(vals), 2) if vals else 0.0


def _winrate(result_list):
    if not result_list:
        return 0.0
    wins = sum(1 for v in result_list if v > 0)
    return round(wins / len(result_list) * 100, 1)


def _grade(t):
    sv  = t.get("setup_valid", False)
    fr  = t.get("followed_rules")
    cr  = t.get("clean_reaction", False)
    nyk = t.get("ny_killzone", False)
    if sv and fr is True and cr and nyk:
        return "A+"
    if sv and fr is True:
        return "A"
    if sv and fr is False:
        return "B"
    if not sv and fr is True:
        return "C"
    return "F"


_LIQ_TYPES = ["asia", "london", "pdh", "pdl", "nwog", "ndog", "ny_am", "other"]


@router.get("/metrics")
def get_metrics():
    try:
        client = get_supabase_client()
        trades = client.table("trades").select("*").execute().data

        valid   = [t for t in trades if t.get("setup_valid")]
        all_r   = [t["result_r"] for t in trades if t.get("result_r") is not None]
        valid_r = [t["result_r"] for t in valid  if t.get("result_r") is not None]

        # ── fase 16: performance data ─────────────────────────────────────────
        winrate_by_liquidity = {
            lt: _winrate([t["result_r"] for t in trades
                          if t.get("liquidity_type") == lt and t.get("result_r") is not None])
            for lt in _LIQ_TYPES
        }

        nyk_r    = [t["result_r"] for t in trades if     t.get("ny_killzone") and t.get("result_r") is not None]
        no_nyk_r = [t["result_r"] for t in trades if not t.get("ny_killzone") and t.get("result_r") is not None]
        cr_r     = [t["result_r"] for t in trades if     t.get("clean_reaction") and t.get("result_r") is not None]
        no_cr_r  = [t["result_r"] for t in trades if not t.get("clean_reaction") and t.get("result_r") is not None]
        fomo_r   = [t["result_r"] for t in trades if t.get("emotional_state") == "fomo"      and t.get("result_r") is not None]
        ans_r    = [t["result_r"] for t in trades if t.get("emotional_state") == "ansioso"   and t.get("result_r") is not None]
        frus_r   = [t["result_r"] for t in trades if t.get("emotional_state") == "frustrado" and t.get("result_r") is not None]

        wn_nyk    = _winrate(nyk_r)
        wn_no_nyk = _winrate(no_nyk_r)
        wn_cr     = _winrate(cr_r)
        wn_no_cr  = _winrate(no_cr_r)
        wn_fomo   = _winrate(fomo_r)
        wn_ans    = _winrate(ans_r)
        wn_frus   = _winrate(frus_r)

        # ── fase 16: insights ────────────────────────────────────────────────
        insights = []
        overall  = _winrate(all_r)

        if len(nyk_r) >= 2 and len(no_nyk_r) >= 2:
            diff = wn_nyk - wn_no_nyk
            if abs(diff) > 10:
                insights.append("Tu winrate es mayor en NY Killzone" if diff > 0
                                 else "Tu winrate es menor en NY Killzone")

        if len(cr_r) >= 2 and len(no_cr_r) >= 2:
            diff = wn_cr - wn_no_cr
            if abs(diff) > 10:
                insights.append("Tus resultados mejoran con clean reaction" if diff > 0
                                 else "Pierdes más cuando no hay clean reaction")

        if len(fomo_r) >= 2 and all_r:
            diff = wn_fomo - overall
            if abs(diff) > 10:
                insights.append("FOMO reduce tu winrate" if diff < 0
                                 else "Tu winrate no se ve afectado negativamente por FOMO")

        if len(ans_r) >= 2 and all_r:
            diff = wn_ans - overall
            if abs(diff) > 10:
                insights.append("La ansiedad reduce tu winrate" if diff < 0
                                 else "La ansiedad no afecta negativamente tu winrate")

        if len(frus_r) >= 2 and all_r:
            diff = wn_frus - overall
            if abs(diff) > 10:
                insights.append("La frustración reduce tu winrate" if diff < 0
                                 else "La frustración no afecta negativamente tu winrate")

        liq_with_data = {lt: wr for lt, wr in winrate_by_liquidity.items() if wr > 0}
        if len(liq_with_data) >= 2:
            best_liq = max(liq_with_data, key=liq_with_data.get)
            insights.append(f"Tus mejores resultados ocurren en {best_liq}")

        if not insights:
            insights.append("No hay suficientes datos para generar insights")

        # ── fase 17: discipline tracking ──────────────────────────────────────
        day_counts = defaultdict(int)
        for t in trades:
            if t.get("trading_day_id") is not None:
                day_counts[t["trading_day_id"]] += 1

        overtrading_days   = sum(1 for cnt in day_counts.values() if cnt > 2)
        avg_trades_per_day = round(len(trades) / len(day_counts), 2) if day_counts else 0.0

        sorted_r = [t["result_r"] for t in sorted(
            [t for t in trades if t.get("result_r") is not None],
            key=lambda t: t.get("created_at", ""),
        )]

        max_win_streak = max_loss_streak = cur_win = cur_loss = 0
        for r in sorted_r:
            if r > 0:
                cur_win  += 1; cur_loss  = 0
                max_win_streak  = max(max_win_streak,  cur_win)
            elif r < 0:
                cur_loss += 1; cur_win   = 0
                max_loss_streak = max(max_loss_streak, cur_loss)
            else:
                cur_win = cur_loss = 0

        if sorted_r:
            current_streak = cur_win if sorted_r[-1] > 0 else (-cur_loss if sorted_r[-1] < 0 else 0)
        else:
            current_streak = 0

        total            = len(trades)
        disciplined_cnt  = sum(1 for t in trades if t.get("setup_valid") and t.get("followed_rules") is True)
        rule_break_cnt   = sum(1 for t in trades if t.get("followed_rules") is False)
        disciplined_ratio = round(disciplined_cnt  / total, 2) if total else 0.0
        rule_break_rate   = round(rule_break_cnt   / total, 2) if total else 0.0

        discipline_alerts = []
        if overtrading_days > 2:
            discipline_alerts.append("Estás sobreoperando")
        if rule_break_rate > 0.3:
            discipline_alerts.append("Estás rompiendo tus reglas frecuentemente")
        if max_loss_streak >= 3:
            discipline_alerts.append("Estás en racha negativa")
        if disciplined_ratio < 0.5:
            discipline_alerts.append("Baja disciplina detectada")
        if not discipline_alerts:
            discipline_alerts.append("Disciplina estable")

        return {
            # ── existing ─────────────────────────────────────────────────────
            "total_trades":               len(trades),
            "valid_setups":               len(valid),
            "invalid_setups":             len(trades) - len(valid),
            "disciplined_trades":         sum(1 for t in trades if t.get("setup_valid") and t.get("followed_rules") is True),
            "discipline_errors":          sum(1 for t in trades if t.get("setup_valid") and t.get("followed_rules") is False),
            "fomo_trades":                sum(1 for t in trades if t.get("emotional_state") == "fomo"),
            "anxiety_trades":             sum(1 for t in trades if t.get("emotional_state") == "ansioso"),
            "fear_exits":                 sum(1 for t in trades if t.get("exit_reason") == "por_miedo"),
            "impulse_exits":              sum(1 for t in trades if t.get("exit_reason") == "por_impulso"),
            "avg_result_r":               _safe_avg(all_r),
            "avg_result_r_valid_setups":  _safe_avg(valid_r),
            "winrate_overall":            _winrate(all_r),
            "winrate_valid_setups":       _winrate(valid_r),

            # ── technical errors ─────────────────────────────────────────────
            "trades_without_sweep":       sum(1 for t in trades if not t.get("sweep_confirmed", False)),
            "trades_without_pda":         sum(1 for t in trades if not t.get("pda_confirmed", False)),
            "trades_without_ifvg":        sum(1 for t in trades if not t.get("ifvg_confirmed", False)),
            "trades_without_vshape":      sum(1 for t in trades if not t.get("vshape_confirmed", False)),
            "trades_unclean_reaction":    sum(1 for t in trades if t.get("setup_valid") and not t.get("clean_reaction", False)),
            "trades_outside_ny_killzone": sum(1 for t in trades if t.get("setup_valid") and not t.get("ny_killzone", False)),

            # ── psychology errors ────────────────────────────────────────────
            "frustration_trades":         sum(1 for t in trades if t.get("emotional_state") == "frustrado"),
            "rule_break_trades":          sum(1 for t in trades if t.get("followed_rules") is False),

            # ── grades ───────────────────────────────────────────────────────
            "grade_a_plus_trades":        sum(1 for t in trades if _grade(t) == "A+"),
            "grade_a_trades":             sum(1 for t in trades if _grade(t) == "A"),
            "grade_b_trades":             sum(1 for t in trades if _grade(t) == "B"),
            "grade_c_trades":             sum(1 for t in trades if _grade(t) == "C"),
            "grade_f_trades":             sum(1 for t in trades if _grade(t) == "F"),

            # ── fase 16: performance analysis ────────────────────────────────
            "winrate_by_liquidity":        winrate_by_liquidity,
            "winrate_ny_killzone":         wn_nyk,
            "winrate_outside_ny_killzone": wn_no_nyk,
            "winrate_clean_reaction":      wn_cr,
            "winrate_unclean_reaction":    wn_no_cr,
            "winrate_fomo":                wn_fomo,
            "winrate_ansiedad":            wn_ans,
            "winrate_frustracion":         wn_frus,
            "performance_insights":        insights,

            # ── fase 17: discipline tracking ─────────────────────────────────
            "overtrading_days":    overtrading_days,
            "avg_trades_per_day":  avg_trades_per_day,
            "max_win_streak":      max_win_streak,
            "max_loss_streak":     max_loss_streak,
            "current_streak":      current_streak,
            "disciplined_ratio":   disciplined_ratio,
            "rule_break_rate":     rule_break_rate,
            "discipline_alerts":   discipline_alerts,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
