from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TradeCreate(BaseModel):
    trading_day_id:   int
    daily_bias_id:    Optional[int] = None
    direction:        str
    sweep_confirmed:  bool = False
    pda_confirmed:    bool = False
    ifvg_confirmed:   bool = False
    vshape_confirmed: bool = False
    smt_confirmed:    bool = False
    clean_reaction:   bool = False
    ny_killzone:      bool = False
    liquidity_type:   Optional[str] = None
    entry_price:      float
    stop_loss:        float
    take_profit:      float
    result_r:         Optional[float] = None
    notes:            Optional[str] = None
    followed_rules:   Optional[bool] = None
    emotional_state:  Optional[str] = None
    exit_reason:      Optional[str] = None


class TradeResponse(BaseModel):
    id:               int
    trading_day_id:   int
    daily_bias_id:    Optional[int]
    direction:        str
    sweep_confirmed:  bool
    pda_confirmed:    bool = False
    ifvg_confirmed:   bool
    vshape_confirmed: bool
    smt_confirmed:    bool
    clean_reaction:   bool = False
    ny_killzone:      bool = False
    liquidity_type:   Optional[str] = None
    setup_valid:      bool
    entry_price:      float
    stop_loss:        float
    take_profit:      float
    result_r:         Optional[float]
    notes:            Optional[str]
    followed_rules:   Optional[bool]
    emotional_state:  Optional[str]
    exit_reason:      Optional[str]
    discipline_label:       Optional[str] = None
    emotional_label:        Optional[str] = None
    exit_label:             Optional[str] = None
    technical_error_label:  Optional[str] = None
    psychology_error_label: Optional[str] = None
    execution_quality_label:Optional[str] = None
    trade_grade:            Optional[str] = None
    created_at:             datetime
