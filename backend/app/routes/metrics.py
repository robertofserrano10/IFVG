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


@router.get("/metrics")
def get_metrics():
    try:
        client = get_supabase_client()
        trades = client.table("trades").select("*").execute().data

        valid   = [t for t in trades if t.get("setup_valid")]
        all_r   = [t["result_r"] for t in trades if t.get("result_r") is not None]
        valid_r = [t["result_r"] for t in valid  if t.get("result_r") is not None]

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
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
