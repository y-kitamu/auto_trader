"""base_trader.py
"""

from ..types import TradeHistory


class BaseTrader:

    def fee_rate(self, symbol: str) -> float:
        raise NotImplementedError

    def buy(self, symbol: str, price: float, volume: float) -> TradeHistory:
        raise NotImplementedError

    def sell(self, symbol: str, price: float, volume: float) -> TradeHistory:
        raise NotImplementedError
