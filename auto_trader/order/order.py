"""order.py
"""

from ..utils import gmo
from .base_order import BaseOrder


class Order(BaseOrder):
    """現物取引の注文を管理するクラス"""

    symbol: str
    side: str
    order_id: int
    losscut_price: float
    close_order_id: int = -1
    closed: bool = False

    @staticmethod
    def new_order(symbol: str, price: float, volume: float, losscut_price: float):
        order = gmo.post_order(symbol, price, volume)
        return Order(
            symbol=symbol,
            order_id=order,
            losscut_price=losscut_price,
            side="BUY" if volume > 0 else "SELL",
        )

    def is_closed(self):
        """注文がすべて終了状態で、持ち高が0の状態の場合はTrue、そうでない場合はFalse"""
        if self.closed:
            return self.closed

        def _is_closed():
            if not gmo.is_order_finished(self.order_id):
                return False  # 注文がまだ有効な場合
            executed = gmo.calc_executed_volume(self.order_id)
            if abs(executed) < 1e-5:
                return True  # 持ち高が0の場合
            if self.close_order_id < 0:
                return False  # 持ち高がある状態で、反対取引が発行されていない
            if not gmo.is_order_finished(self.close_order_id):
                return False  # 反対取引が有効な場合
            executed -= gmo.calc_executed_volume(self.close_order_id)
            if abs(executed) < 1e-5:
                return True  # 反対取引が約定済みで持ち高が0の場合
            return False  # 反対取引は約定済みだが持ち高がまだある場合

        self.closed = _is_closed()
        return self.closed

    def losscut(self):
        """losscutを実行する
        Return:
            bool : Trueの場合は持ち高精算済み、そうでない場合（losscut注文発行）はFalse
        """
        self.cancel_order()  # 注文が有効な場合はキャンセル
        executed = gmo.calc_executed_volume(self.order_id)

        if self.close_order_id > 0:  # 反対取引の注文が発行されている場合
            self.cancel_order(self.close_order_id)
            executed -= gmo.calc_executed_volume(self.order_id)

        if abs(executed) < 1e-5:
            self.closed = True
            return True
        self.close_order_id = gmo.post_order(
            symbol=self.symbol, price=-1.0, volume=-executed
        )  # losscutは成り行きで実行
        return False

    def check_losscut(self, current_price: float):
        """losscutの条件を満たしているか確認し、満たしている場合はlosscutを実行する"""
        if self.is_closed():
            return

        if current_price < self.losscut_price:
            self.losscut()

    def cancel_order(self, order_id=None):
        """注文をキャンセルする"""
        if order_id is None:
            order_id = self.order_id
        if not gmo.is_order_finished(order_id):
            gmo.private_api("/v1/cancelOrder", parameters={"orderId": order_id}, method="POST")

    def update_target_price(self, target_price: float):
        """利益確定注文の価格を変更する"""
        if self.is_closed():
            return

        executed = gmo.calc_executed_volume(self.order_id)
        if self.close_order_id > 0:
            self.cancel_order(self.close_order_id)
            executed -= gmo.calc_executed_volume(self.close_order_id)

        self.close_order_id = gmo.post_order(self.symbol, target_price, executed)["data"]["orderId"]

    def summary(self):
        executions = []
        res = gmo.private_api("/v1/executions", parameters={"orderId": self.order_id}, method="POST")
        executions += res["data"]["list"]

        if self.close_order_id > 0:
            res = gmo.private_api(
                "/v1/executions",
                parameters={"orderId": self.close_order_id},
                method="POST",
            )
            executions += res["data"]["list"]
        return executions
