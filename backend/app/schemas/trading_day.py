# Schemas Pydantic para la tabla trading_days.
# TradingDayCreate: datos que llegan en el POST (sin id ni created_at).
# TradingDayResponse: datos que devuelve la API al cliente.

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class TradingDayCreate(BaseModel):
    trade_date: date
    market: str
    is_news_day: bool = False
    is_ath_context: bool = False
    notes: Optional[str] = None


class TradingDayResponse(BaseModel):
    id: int
    trade_date: date
    market: str
    is_news_day: bool
    is_ath_context: bool
    notes: Optional[str]
    created_at: datetime
