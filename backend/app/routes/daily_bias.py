# Rutas para la tabla daily_bias.
# GET /daily-bias  → devuelve todos los registros ordenados por created_at descendente.
# POST /daily-bias → inserta un nuevo registro en Supabase.

from typing import List

from fastapi import APIRouter, HTTPException

from app.database import get_supabase_client
from app.schemas.daily_bias import DailyBiasCreate, DailyBiasResponse

router = APIRouter()


@router.get("/daily-bias", response_model=List[DailyBiasResponse])
def get_daily_bias():
    try:
        client = get_supabase_client()
        response = (
            client.table("daily_bias")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daily-bias", response_model=DailyBiasResponse, status_code=201)
def create_daily_bias(payload: DailyBiasCreate):
    try:
        client = get_supabase_client()
        response = client.table("daily_bias").insert(payload.model_dump()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/daily-bias/{bias_id}")
def delete_daily_bias(bias_id: int):
    try:
        client = get_supabase_client()
        existing = client.table("daily_bias").select("id").eq("id", bias_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail=f"Daily bias {bias_id} not found")
        client.table("daily_bias").delete().eq("id", bias_id).execute()
        return {"deleted": True, "daily_bias_id": bias_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
