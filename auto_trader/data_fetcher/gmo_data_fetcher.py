"""gmo_data_fetcher.py
"""

import datetime
import json
import threading

import websocket

from ..base import BaseDataFetcher
from ..types import TickData


class GMODataFetcher(BaseDataFetcher):

    def __init__(self, symbol: str):
        super().__init__(symbol)
        self.thread, self.ws = None, None

    def start_subscribe(self):
        symbol = self._symbol

        def on_open(self):
            message = {"command": "subscribe", "channel": "trades", "symbol": symbol}
            self.send(json.dumps(message))

        que = self._que

        def on_message(self, message):
            data = json.loads(message)
            if data["side"] == "BUY":
                que.put(
                    TickData(
                        side=data["side"],
                        symbol=data["symbol"],
                        price=data["price"],
                        volume=data["size"],
                        timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
                    )
                )

        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp("wss://api.coin.z.com/ws/public/v1")
        self.ws.on_open = on_open
        self.ws.on_message = on_message
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.start()

    def stop_subscribe(self):
        if self.ws is None or self.thread is None:
            return
        self.ws.keep_running = False
        self.thread.join()
