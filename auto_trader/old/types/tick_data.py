"""tick_data.py
"""

import datetime

from pydantic import BaseModel


class TickData(BaseModel):
    side: str
    symbol: str
    price: float
    volume: float
    timestamp: datetime.datetime
