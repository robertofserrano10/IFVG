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


@router.get("/metrics")
def get_metrics():
    try:
        client = get_supabase_client()
        trades = client.table("trades").select("*").execute().data

        valid   = [t for t in trades if t.get("setup_valid")]
        all_r   = [t["result_r"] for t in trades if t.get("result_r") is not None]
        valid_r = [t["result_r"] for t in valid  if t.get("result_r") is not None]

        return {
            "total_trades":              len(trades),
            "valid_setups":              len(valid),
            "invalid_setups":            len(trades) - len(valid),
            "disciplined_trades":        sum(1 for t in trades if t.get("setup_valid") and t.get("followed_rules") is True),
            "discipline_errors":         sum(1 for t in trades if t.get("setup_valid") and t.get("followed_rules") is False),
            "fomo_trades":               sum(1 for t in trades if t.get("emotional_state") == "fomo"),
            "anxiety_trades":            sum(1 for t in trades if t.get("emotional_state") == "ansioso"),
            "fear_exits":                sum(1 for t in trades if t.get("exit_reason") == "por_miedo"),
            "impulse_exits":             sum(1 for t in trades if t.get("exit_reason") == "por_impulso"),
            "avg_result_r":              _safe_avg(all_r),
            "avg_result_r_valid_setups": _safe_avg(valid_r),
            "winrate_overall":           _winrate(all_r),
            "winrate_valid_setups":      _winrate(valid_r),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
