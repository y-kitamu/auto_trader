"""wallet.py
"""

from pydantic import BaseModel

from ..base import BaseWallet
from ..types import Order, TradeHistory


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
        print(f"current cash : {self.current_cash}")
        for pos in self.current_positions:
            print(f"pos: {pos}, {current_prices[pos.symbol] * pos.volume}}}")
            total_assets += current_prices[pos.symbol] * pos.volume
        return total_assets

    def calc_trade_volume(self, symbol: str, price: float, volume: float, fee: float) -> float:
        """要求されたトレードの取引量に対して、実際に取引可能な量を計算して返す"""
        tradable_volume = 0  # 取引可能量
        for pos in self.current_positions:
            if (pos.symbol == symbol) and pos.volume * volume < 0:
                tradable_volume = (
                    -pos.volume * 2
                )  # 反対トレード + （反対トレードで得た資金を使った）新規トレード
                if abs(volume) < abs(tradable_volume):
                    tradable_volume = volume
                break

        if abs(tradable_volume) < abs(volume):
            cost = price * abs(volume - tradable_volume) * (1.0 + fee)
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

    def update_wallet(self, order: Order):
        position = self.get_target_position(order.symbol)
        # positionの増減
        position.volume += order.volume
        # 現金の増減
        self.current_cash -= order.volume * order.price
        # 手数料
        fee = abs(order.volume) * order.price * order.fee
        self.current_cash -= fee
        if self.current_cash < 0:
            raise RuntimeError("Failed to update wallet")

        print(f"Update wallet: {position}, {self.current_cash}, {fee}")
