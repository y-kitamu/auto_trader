"""base_trader.py
"""
import datetime

from ..types import TradeHistory


class BaseTrader:

    def fee_rate(self, symbol: str) -> float:
        raise NotImplementedError

    def buy_order(self, symbol: str, price: float, volume: float, deadline: datetime.datetime) -> TradeHistory:
        raise NotImplementedError

    def sell_order(self, symbol: str, price: float, volume: float, deadline: datetime.datetime) -> TradeHistory:
        raise NotImplementedError
