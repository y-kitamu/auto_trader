"""base_data_fetcher.py
"""

import queue

from ..types import TickData


class BaseDataFetcher:

    def __init__(self, symbol):
        self._symbol = symbol
        self._que = queue.Queue()

    @property
    def que(self) -> queue.Queue[TickData]:
        return self._que

    def start_subscribe(self):
        raise NotImplementedError

    def stop_subscribe(self):
        raise NotImplementedError
