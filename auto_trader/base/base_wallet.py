"""base_wallet.py
"""

from ..types import TradeHistory


class BaseWallet:

    def get_current_total_assets(self, current_prices: dict[str, float]) -> float:
        raise NotImplementedError

    def calc_trade_volume(self, symbol: str, price: float, volume: float, fee: float) -> float:
        raise NotImplementedError

    def update_wallet(self, trade: TradeHistory):
        raise NotImplementedError
