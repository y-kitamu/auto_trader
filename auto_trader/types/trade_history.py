"""trade_history.py
"""

import datetime
from typing import Self

from pydantic import BaseModel


class TradeHistory(BaseModel):
    symbol: str
    price: float
    volume: float  # positive value:  buy, negative value: sell
    fee: float
    timestamp: datetime.datetime
    settlement_trade: Self | None = None
