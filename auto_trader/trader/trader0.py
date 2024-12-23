"""trader0.py
"""

import asyncio
import datetime
import pickle
import time
from pathlib import Path

import polars as pl

import stock
from ..logging import enable_logging_to_file, logger
from ..order import BaseOrder, LeverageOrder, Order
from ..utils import gmo, history

train_features = sorted(
    [
        "ADX",
        "ADXR",
        "APO",
        "AROON_aroondown",
        "AROON_aroonup",
        "AROONOSC",
        "CCI",
        "DX",
        "MACD_macd",
        "MACD_macdsignal",
        "MACD_macdhist",
        "MFI",
        #     'MINUS_DI',
        #     'MINUS_DM',
        "MOM",
        #     'PLUS_DI',
        #     'PLUS_DM',
        "RSI",
        "STOCH_slowk",
        "STOCH_slowd",
        "STOCHF_fastk",
        #     'STOCHRSI_fastd',
        "ULTOSC",
        "WILLR",
        #     'ADOSC',
        #     'NATR',
        "HT_DCPERIOD",
        "HT_DCPHASE",
        "HT_PHASOR_inphase",
        "HT_PHASOR_quadrature",
        "HT_TRENDMODE",
        "BETA",
        "LINEARREG",
        "LINEARREG_ANGLE",
        "LINEARREG_INTERCEPT",
        "LINEARREG_SLOPE",
        "STDDEV",
        "BBANDS_upperband",
        "BBANDS_middleband",
        "BBANDS_lowerband",
        "DEMA",
        "EMA",
        "HT_TRENDLINE",
        "KAMA",
        "MA",
        "MIDPOINT",
        "T3",
        "TEMA",
        "TRIMA",
        "WMA",
    ]
)


def fetch_df(
    symbol: str,
    interval: datetime.timedelta,
    start_date: datetime.datetime = datetime.datetime.now(),
    min_length: int = 30,
):
    df = gmo.get_ohlc(symbol, interval, date=start_date)
    while len(df) < min_length:
        start_date -= datetime.timedelta(days=1)
        df = df.vstack(gmo.get_ohlc(symbol, interval, date=start_date))
    df = df.sort(pl.col("datetime")).with_columns(
        pl.col("open").cast(pl.Float64),
        pl.col("high").cast(pl.Float64),
        pl.col("low").cast(pl.Float64),
        pl.col("close").cast(pl.Float64),
        pl.col("volume").cast(pl.Float64),
    )
    return df


class Trader0:

    def __init__(
        self,
        symbol: str,
        interval: datetime.timedelta,
        model_path: Path,
        log_dir: Path,
        wait_second: int = 1,
        data_length: int = 100,
        volume: float = 0.01,
    ):
        self.ORDER_TYPE = LeverageOrder if symbol in gmo.LEVERAGE_SYMBOLS else Order
        self.leverage = 2 if symbol in gmo.LEVERAGE_SYMBOLS else 1
        self.symbol = symbol
        self.interval = interval
        self.data_length = data_length
        current = datetime.datetime.now()
        interval_minutes = int(interval / datetime.timedelta(minutes=1))
        next_wall_minute = (current.minute // interval_minutes + 1) * interval_minutes
        offset = 1 if next_wall_minute > 59 else 0
        next_wall_minute = next_wall_minute % 60
        self.next_wall = datetime.datetime(
            year=current.year,
            month=current.month,
            day=current.day,
            hour=current.hour + offset,
            minute=next_wall_minute,
        )
        self.orders: list[BaseOrder] = []
        self.wait_second = wait_second
        self.log_dir = log_dir
        self.volume = volume

        self.is_running = False

        # modelの読み込み
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

    def losscut(self):
        """毎ステップ実行するlosscutチェック"""
        # 最新の価格を更新
        latest_data = gmo.public_api("/v1/ticker")["data"]
        for order in self.orders:
            for data in latest_data:
                if data["symbol"] == order.symbol:
                    order.check_losscut(float(data["last"]))
                    break

    def get_order_volume(self, price: float) -> float:
        """注文する数量を返す"""
        res = gmo.private_api("/v1/account/margin", parameters={}, method="GET")
        if float(res["data"]["availableAmount"]) * self.leverage > self.volume * price:
            return self.volume
        return 0.0

    def on_new_tick_added(self):
        """新しい価格データが追加された際の処理"""
        # 特徴量の計算、モデルの実行
        df = fetch_df(self.symbol, self.interval, min_length=self.data_length).sort(pl.col("datetime"))[
            -self.data_length - 1 : -1
        ]
        df = stock.crypto.feature.calc_features(df)
        feat = df.select(*train_features).to_numpy()
        preds = self.model.predict(feat)

        # 発注済みの注文の目標株価を更新
        target_buy_price = df["close"][-1] - df["ATR"][-1] * 0.8
        target_sell_price = df["close"][-1] + df["ATR"][-1] * 0.8
        for order in self.orders:
            order.cancel_order()  # 既存の新規注文はキャンセル
            if order.side == "BUY":
                order.update_target_price(target_sell_price)
            else:
                order.update_target_price(target_buy_price)

        if preds[-1] > 0:  # モデルのスコアが良い場合は新規注文
            volume = self.get_order_volume(target_buy_price)
            if volume > 1e-5:
                self.orders.append(
                    self.ORDER_TYPE.new_order(
                        symbol=self.symbol,
                        price=target_buy_price,
                        volume=volume,
                        losscut_price=target_buy_price * 0.92,
                    )
                )

    def run_loop(self):
        self.is_running = True
        date_str = datetime.datetime.now().isoformat()
        trade_history_csv = self.log_dir / f"trade_history_{date_str}.csv"
        enable_logging_to_file(self.log_dir / f"trader_{date_str}.log")
        logger.debug("Start auto trade")
        # fut = asyncio.sleep(self.wait_second)
        while self.is_running:
            self.losscut()  # losscutのチェック
            # next wallに到達した場合の処理
            if self.next_wall < datetime.datetime.now():
                self.next_wall += self.interval  # next wallの更新
                self.on_new_tick_added()

            closed_orders = [order for order in self.orders if order.is_closed()]
            self.orders = [order for order in self.orders if not order.is_closed()]
            history.log_closed_order(closed_orders, trade_history_csv)

            # loop頻度制御
            # await fut
            # fut = asyncio.sleep(self.wait_second)
            time.sleep(self.wait_second)

        self.cancel_all_orders()
        history.log_closed_order(self.orders, trade_history_csv)
        logger.debug("Stop auto trade")

    def cancel_all_orders(self):
        is_closed = False
        while not is_closed:
            is_closed = True
            for order in self.orders:
                order.cancel_order()
                order.losscut()
                is_closed &= order.is_closed()

    def stop_loop(self):
        self.is_running = False
