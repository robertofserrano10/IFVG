from datetime import datetime
from pydantic import BaseModel


class TradeImageCreate(BaseModel):
    trade_id:   int
    image_url:  str
    image_type: str  # entrada | salida | contexto


class TradeImageResponse(BaseModel):
    id:         int
    trade_id:   int
    image_url:  str
    image_type: str
    created_at: datetime
