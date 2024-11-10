"""base_strategy.py
"""

from ..types import TickData


class BaseStrategy:
    @property
    def wallet(self):
        return self._wallet

    def add_new_data(self, data: TickData):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError
