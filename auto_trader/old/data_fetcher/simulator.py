"""simulator.py
"""

import asyncio
import threading

import polars as pl

from ..base import BaseDataFetcher
from ..types import TickData


class SimulatorDataFetcher(BaseDataFetcher):

    def __init__(self, symbol, df: pl.DataFrame, loop_interval: float = 0.5):
        super().__init__(symbol)
        self._df = df.sort(pl.col("datetime"))
        self._interval = loop_interval
        self._thread = None
        self._running = False

    def start_subscribe(self):
        self._running = True

        async def run():
            for i in range(len(self._df)):
                fut = asyncio.sleep(self._interval)
                self._que.put(
                    TickData(
                        side=self._df["side"][i],
                        symbol=self._df["symbol"][i],
                        price=self._df["price"][i],
                        volume=self._df["size"][i],
                        timestamp=self._df["datetime"][i],
                    )
                )
                await fut
                if not self._running:
                    break

        self._thread = threading.Thread(target=asyncio.run, args=(run(),))
        self._thread.start()

    def stop_subscribe(self):
        self._running = False
        if self._thread is not None:
            self._thread.join()
        print("Simulator stopped.")
