"""base_order.py
"""

from pydantic import BaseModel


class BaseOrder(BaseModel):
    symbol: str
    side: str
    closed: bool = False

    @staticmethod
    def new_order(symbol: str, price: float, volume: float, losscut_price: float):
        raise NotImplementedError

    def is_closed(self):
        raise NotImplementedError

    def losscut(self):
        raise NotImplementedError

    def cancel_order(self, order_id: str | None = None):
        raise NotImplementedError

    def check_losscut(self, current_price: float):
        raise NotImplementedError

    def update_target_price(self, target_price: float):
        raise NotImplementedError

    def summary(self):
        raise NotImplementedError

    def __del__(self):
        # object消滅時には注文をキャンセルする
        self.cancel_order()
        self.losscut()
