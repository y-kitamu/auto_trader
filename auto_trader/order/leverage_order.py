"""leverage_order.py
"""

from ..logging import logger
from ..utils import gmo
from .base_order import BaseOrder


class LeverageOrder(BaseOrder):
    """信用取引の注文を管理するクラス"""

    symbol: str
    side: str
    order_id: str
    losscut_price: float
    close_order_ids: list[str] = []
    closed: bool = False

    @staticmethod
    def new_order(symbol: str, price: float, volume: float, losscut_price: float):
        order = gmo.post_order(symbol, price, volume)
        logger.info(
            f"New order : symbol = {symbol}, price = {price}, volume = {volume}, order_id = {order['data']}"
        )
        return LeverageOrder(
            symbol=symbol,
            order_id=order["data"],
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
            if len(gmo.get_open_positions(self.order_id)) > 0:
                return False  # positionが残っている場合
            return True

        self.closed = _is_closed()
        return self.closed

    def losscut(self):
        """losscutを実行する
        Return:
            bool : Trueの場合は持ち高精算済み、そうでない場合（losscut注文発行）はFalse
        """
        self.cancel_order()  # 注文が有効な場合はキャンセル

        if len(self.close_order_ids) > 0:  # 反対取引の注文が発行されている場合
            for order in self.close_order_ids:
                self.cancel_order(order)

        open_positions = gmo.get_open_positions(self.order_id)
        if len(open_positions) == 0:
            self.closed = True
            return True

        for pos in open_positions:
            res = gmo.post_leverage_close_order(
                symbol=pos["symbol"],
                price=-1.0,
                volume=pos["size"],
                position_id=pos["positionId"],
                side="SELL" if pos["side"] == "BUY" else "BUY",
            )
            self.close_order_ids.append(res["data"]["orderId"])

        logger.info(
            "losscut order issued : original order_id = {}, close_order_ids = {}".format(
                self.order_id, ", ".join(self.close_order_ids)
            )
        )
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
            logger.debug("Order canceled : order_id = {}".format(order_id))

    def update_target_price(self, target_price: float):
        """利益確定注文の価格を変更する"""
        if self.is_closed():
            return

        # 注文中の決済取引を一旦全てキャンセル
        for order in self.close_order_ids:
            self.cancel_order(order)

        # 現在の未決済ポジションを取得
        open_positions = gmo.get_open_positions(self.order_id)
        if len(open_positions) == 0:
            return

        # 決済取引を再度発行
        for pos in open_positions:
            self.close_order_ids.append(
                gmo.post_leverage_close_order(
                    symbol=pos["symbol"],
                    price=target_price,
                    volume=pos["size"],
                    position_id=pos["positionId"],
                    side="SELL" if pos["side"] == "BUY" else "BUY",
                )["data"]
            )
            logger.debug(
                "Update target price : order_id = {}, target_price = {}, volume = {}, position_id = {}".format(
                    self.order_id, target_price, pos["size"], pos["positionId"]
                )
            )

    def summary(self):
        executions = []
        res = gmo.private_api("/v1/executions", parameters={"orderId": self.order_id}, method="GET")
        if "list" in res["data"]:
            executions += res["data"]["list"]

        for order_id in self.close_order_ids:
            res = gmo.private_api(
                "/v1/executions",
                parameters={"orderId": order_id},
                method="GET",
            )
            if "list" in res["data"]:
                executions += res["data"]["list"]

        return executions
