# Schemas Pydantic para la tabla daily_bias.
# DailyBiasCreate: datos que llegan en el POST.
# DailyBiasResponse: datos que devuelve la API al cliente.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DailyBiasCreate(BaseModel):
    trading_day_id: int
    daily_high: float
    daily_low: float
    daily_eq: float
    current_price: float
    zone_position: str
    asia_high: float
    asia_low: float
    london_high: float
    london_low: float
    pending_liquidity_direction: str
    premium_discount_direction: str
    bias_alignment: bool = False
    bias_direction: str
    bias_active: bool = True
    chop_equilibrium: bool = False
    invalidated: bool = False
    invalidation_reason: Optional[str] = None
    comments: Optional[str] = None


class DailyBiasResponse(BaseModel):
    id: int
    trading_day_id: int
    daily_high: float
    daily_low: float
    daily_eq: float
    current_price: float
    zone_position: str
    asia_high: float
    asia_low: float
    london_high: float
    london_low: float
    pending_liquidity_direction: str
    premium_discount_direction: str
    bias_alignment: bool
    bias_direction: str
    bias_active: bool
    chop_equilibrium: bool
    invalidated: bool
    invalidation_reason: Optional[str]
    comments: Optional[str]
    created_at: datetime
