"""gmo_trader.py
"""

import datetime

from ..base import BaseTrader
from ..types import TradeHistory


class GMOTrader(BaseTrader):
    def buy_order(self, symbol: str, price: float, volume: float, deadline: datetime.datetime):
        return TradeHistory(symbol=symbol, price=price, volume=volume, timestamp=datetime.datetime.now())

    def sell_order(self, symbol: str, price: float, volume: float, deadline: datetime.datetime):
        return TradeHistory(symbol=symbol, price=price, volume=volume, timestamp=datetime.datetime.now())
