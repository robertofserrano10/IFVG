# Rutas para la tabla trading_days.
# GET /trading-days  → devuelve todos los registros ordenados por fecha descendente.
# POST /trading-days → inserta un nuevo registro en Supabase.

from typing import List

from fastapi import APIRouter, HTTPException

from app.database import get_supabase_client
from app.schemas.trading_day import TradingDayCreate, TradingDayResponse

router = APIRouter()


@router.get("/trading-days", response_model=List[TradingDayResponse])
def get_trading_days():
    try:
        client = get_supabase_client()
        response = (
            client.table("trading_days")
            .select("*")
            .order("trade_date", desc=True)
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trading-days", response_model=TradingDayResponse, status_code=201)
def create_trading_day(payload: TradingDayCreate):
    try:
        client = get_supabase_client()
        # model_dump() convierte el objeto Pydantic a dict.
        # trade_date se convierte a string porque Supabase espera "YYYY-MM-DD".
        data = payload.model_dump()
        data["trade_date"] = str(data["trade_date"])
        response = client.table("trading_days").insert(data).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
