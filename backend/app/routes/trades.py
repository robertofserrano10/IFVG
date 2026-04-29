from typing import List

from fastapi import APIRouter, HTTPException

from app.database import get_supabase_client
from app.schemas.trade import TradeCreate, TradeResponse

router = APIRouter()


def _add_labels(trade: dict) -> dict:
    setup_valid      = trade.get("setup_valid", False)
    followed_rules   = trade.get("followed_rules")
    emotional_state  = trade.get("emotional_state")
    exit_reason      = trade.get("exit_reason")
    sweep_confirmed  = trade.get("sweep_confirmed", False)
    ifvg_confirmed   = trade.get("ifvg_confirmed", False)
    vshape_confirmed = trade.get("vshape_confirmed", False)
    pda_confirmed    = trade.get("pda_confirmed", False)
    clean_reaction   = trade.get("clean_reaction", False)
    ny_killzone      = trade.get("ny_killzone", False)

    # ── discipline_label (existing) ──────────────────────────────────────────
    if not setup_valid:
        if sweep_confirmed and ifvg_confirmed and vshape_confirmed and not pda_confirmed:
            trade["discipline_label"] = "Setup inválido: faltó PDA HTF"
        else:
            trade["discipline_label"] = "Setup inválido"
    elif followed_rules is True:
        trade["discipline_label"] = "Trade disciplinado"
    elif followed_rules is False:
        trade["discipline_label"] = "Error de disciplina"
    else:
        trade["discipline_label"] = None

    # ── emotional_label (existing) ───────────────────────────────────────────
    trade["emotional_label"] = (
        "Trade emocional (FOMO)" if emotional_state == "fomo"    else
        "Trade con ansiedad"     if emotional_state == "ansioso" else
        None
    )

    # ── exit_label (existing) ────────────────────────────────────────────────
    trade["exit_label"] = (
        "Salida por miedo"   if exit_reason == "por_miedo"   else
        "Salida por impulso" if exit_reason == "por_impulso" else
        None
    )

    # ── technical_error_label ────────────────────────────────────────────────
    if not sweep_confirmed:
        technical = "Error técnico: entrada sin sweep"
    elif not pda_confirmed:
        technical = "Error técnico: faltó PDA HTF"
    elif not ifvg_confirmed:
        technical = "Error técnico: entrada sin IFVG"
    elif not vshape_confirmed:
        technical = "Error técnico: faltó V-Shape"
    elif setup_valid and not clean_reaction:
        technical = "Advertencia técnica: reacción no limpia"
    elif setup_valid and not ny_killzone:
        technical = "Advertencia técnica: fuera de Killzone NY"
    else:
        technical = "Sin error técnico crítico"
    trade["technical_error_label"] = technical

    # ── psychology_error_label ───────────────────────────────────────────────
    if emotional_state == "fomo":
        psychology = "Error psicológico: FOMO"
    elif emotional_state == "ansioso":
        psychology = "Error psicológico: ansiedad"
    elif emotional_state == "frustrado":
        psychology = "Error psicológico: frustración"
    elif followed_rules is False:
        psychology = "Error psicológico: rompió reglas"
    elif exit_reason == "por_miedo":
        psychology = "Error psicológico: salida por miedo"
    elif exit_reason == "por_impulso":
        psychology = "Error psicológico: salida por impulso"
    else:
        psychology = "Sin error psicológico crítico"
    trade["psychology_error_label"] = psychology

    # ── execution_quality_label + trade_grade ────────────────────────────────
    if setup_valid and followed_rules is True and clean_reaction and ny_killzone:
        quality, grade = "Ejecución A+", "A+"
    elif setup_valid and followed_rules is True:
        quality, grade = "Ejecución correcta", "A"
    elif setup_valid and followed_rules is False:
        quality, grade = "Setup válido con mala disciplina", "B"
    elif not setup_valid and followed_rules is True:
        quality, grade = "Buena disciplina, mal setup", "C"
    else:
        quality, grade = "Mal setup y mala disciplina", "F"
    trade["execution_quality_label"] = quality
    trade["trade_grade"] = grade

    return trade


@router.get("/trades", response_model=List[TradeResponse])
def get_trades():
    try:
        client = get_supabase_client()
        response = (
            client.table("trades")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return [_add_labels(t) for t in response.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trades", response_model=TradeResponse, status_code=201)
def create_trade(payload: TradeCreate):
    try:
        client = get_supabase_client()
        data = payload.model_dump()
        data["setup_valid"] = (
            data["sweep_confirmed"] and
            data["pda_confirmed"] and
            data["ifvg_confirmed"] and
            data["vshape_confirmed"]
        )
        response = client.table("trades").insert(data).execute()
        return _add_labels(response.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/trades/{trade_id}")
def delete_trade(trade_id: int):
    try:
        client = get_supabase_client()
        existing = client.table("trades").select("id").eq("id", trade_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
        client.table("trade_images").delete().eq("trade_id", trade_id).execute()
        client.table("trades").delete().eq("id", trade_id).execute()
        return {"deleted": True, "trade_id": trade_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
