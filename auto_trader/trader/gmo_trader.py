"""gmo_trader.py

Author : Yusuke Kitamura
Create Date : 2024-11-09 17:14:20
Copyright (c) 2019- Yusuke Kitamura <ymyk6602@gmail.com>
"""

from ..base import BaseTrader


class GMOTrader(BaseTrader):
    def buy(self, symbol: str, price: float, volume: float):
        pass

    def sell(self, symbol: str, price: float, volume: float):
        pass
