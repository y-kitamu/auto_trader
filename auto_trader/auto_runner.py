"""auto_trader.py
"""

import asyncio

from .base import BaseDataFetcher, BaseStrategy


class AutoRunner:
    def __init__(
        self,
        strategy_list: list[BaseStrategy],
        data_fetcher: BaseDataFetcher,
        loop_interval: float = 0.5,
    ):
        self.data_fetcher = data_fetcher
        self.strategy_list = strategy_list
        self.loop_interval = loop_interval
        self.is_running = False

    async def run_event_loop(self):
        self.is_running = True
        self.data_fetcher.start_subscribe()
        while self.is_running:
            fut = asyncio.sleep(self.loop_interval)
            self.run_step()
            await fut

    def run_step(self):
        while not self.data_fetcher.que.empty():
            data = self.data_fetcher.que.get()
            for strategy in self.strategy_list:
                strategy.add_new_data(data)

        for strategy in self.strategy_list:
            strategy.run()

    def stop_event_loop(self):
        for strategy in self.strategy_list:
            strategy.stop()
        self.data_fetcher.stop_subscribe()
        print("Event loop stopped.")
