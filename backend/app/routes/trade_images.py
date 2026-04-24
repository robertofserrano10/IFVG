from typing import List

from fastapi import APIRouter, HTTPException

from app.database import get_supabase_client
from app.schemas.trade_image import TradeImageCreate, TradeImageResponse

router = APIRouter()


@router.get("/trade-images", response_model=List[TradeImageResponse])
def get_trade_images():
    try:
        client = get_supabase_client()
        response = (
            client.table("trade_images")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trade-images", response_model=TradeImageResponse, status_code=201)
def create_trade_image(payload: TradeImageCreate):
    try:
        client = get_supabase_client()
        response = client.table("trade_images").insert(payload.model_dump()).execute()
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
