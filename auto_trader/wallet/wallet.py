"""wallet.py
"""

from pydantic import BaseModel

from ..base import BaseWallet
from ..types import TradeHistory


class Position(BaseModel):
    symbol: str
    volume: float  # positive value: long position, negative value: short position


class Wallet(BaseWallet):
    def __init__(self, initial_cash: float):
        self.initial_cash = initial_cash
        self.current_cash = initial_cash
        self.current_positions: list[Position] = []

    def get_current_total_assets(self, current_prices: dict[str, float]) -> float:
        total_assets = self.current_cash
        for pos in self.current_positions:
            total_assets += current_prices[pos.symbol] * pos.volume
        return total_assets

    def calc_trade_volume(self, symbol: str, price: float, volume: float, fee: float) -> float:
        """要求されたトレードの取引量に対して、実際に取引可能な量を計算して返す"""
        tradable_volume = 0  # 取引可能量
        for pos in self.current_positions:
            if (pos.symbol == symbol) and pos.volume * volume < 0:
                tradable_volume = (
                    pos.volume * 2
                )  # 反対トレード + （反対トレードで得た資金を使った）新規トレード
                break

        if tradable_volume < volume:
            cost = price * (volume - tradable_volume) * (1.0 + fee)
            if cost <= self.current_cash:
                tradable_volume = volume

        return tradable_volume

    def get_target_position(self, symbol: str) -> Position:
        for pos in self.current_positions:
            if pos.symbol == symbol:
                return pos

        position = Position(symbol=symbol, volume=0)
        self.current_positions.append(position)
        return position

    def update_wallet(self, trade: TradeHistory):
        position = self.get_target_position(trade.symbol)
        # positionの増減
        position.volume -= trade.volume
        # 現金の増減
        self.current_cash += trade.volume * trade.price
        # 手数料
        fee = abs(trade.volume) * trade.price * trade.fee
        self.current_cash -= fee
        if self.current_cash < 0:
            raise RuntimeError("Failed to update wallet")
