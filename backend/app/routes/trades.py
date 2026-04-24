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

    trade["emotional_label"] = (
        "Trade emocional (FOMO)" if emotional_state == "fomo"    else
        "Trade con ansiedad"     if emotional_state == "ansioso" else
        None
    )

    trade["exit_label"] = (
        "Salida por miedo"   if exit_reason == "por_miedo"   else
        "Salida por impulso" if exit_reason == "por_impulso" else
        None
    )

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
