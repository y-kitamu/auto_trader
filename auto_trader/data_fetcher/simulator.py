"""simulator.py
"""

import threading

import polars as pl

from ..base import BaseDataFetcher


class SimulatorDataFetcher(BaseDataFetcher):

    def __init__(self, symbol, df: pl.DataFrame):
        super().__init__(symbol)
        self._df = df.sort(pl.col("datetime"))

    def start_subscribe(self):

        def load_data():
            for i in range(len(self._df)):
                self._que.put(self._df[i].to_dict())

        pass

    def end_subscribe(self):
        pass
