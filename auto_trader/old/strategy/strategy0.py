"""strategy0.py
"""

import datetime

import numpy as np
import polars as pl
from sklearn.base import RegressorMixin
from stock.crypto.feature import calc_features

from ..base import BaseStrategy, BaseTrader, BaseWallet
from ..types import TickData
from ..utils import gmo

# from ..utils.feature import calc_features


def fetch_initial_df(
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


def push_back_data(arr: np.ndarray, val):
    arr = np.roll(arr, -1)
    arr[-1] = val
    return arr


class Strategy0(BaseStrategy):
    """ """

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

    def __init__(
        self,
        symbol: str,
        interval: datetime.timedelta,  # ohlcの時間間隔
        wallet: BaseWallet,
        trader: BaseTrader,
        estimator: RegressorMixin,
        start_date: datetime.datetime = datetime.datetime.now(),
    ):
        self._symbol = symbol
        self._interval = interval
        self._wallet = wallet
        self._trader = trader
        self._estimator = estimator

        df = fetch_initial_df(symbol, interval, start_date=start_date).sort(
            "datetime"
        )  # .select("open", "high", "low", "close", "datetime").sort("datetime")
        self._open = df["open"].to_numpy()
        self._high = df["high"].to_numpy()
        self._low = df["low"].to_numpy()
        self._close = df["close"].to_numpy()
        self._volume = df["volume"].to_numpy()

        self._next_wall = df["datetime"][-1] + self._interval  # 次のbarの終了時刻
        self._next_data_list = []  # 次のbarに含まれるtick data (date, price, volume)

    @property
    def df(self):
        return pl.DataFrame(
            {
                "open": self._open,
                "high": self._high,
                "low": self._low,
                "close": self._close,
                "volume": self._volume,
            }
        )

    def add_new_data(self, data: TickData):
        print("New data : {}".format(data))
        tick_date = data.timestamp
        while tick_date >= self._next_wall:
            if len(self._next_data_list) > 0:
                # 次のbarのohlcを計算
                volume = sum([d[2] for d in self._next_data_list])
                high = max([d[1] for d in self._next_data_list])
                low = min([d[1] for d in self._next_data_list])
                open = self._next_data_list[0][1]
                close = self._next_data_list[-1][1]
                # 配列を更新
                self._open = push_back_data(self._open, open)
                self._high = push_back_data(self._high, high)
                self._low = push_back_data(self._low, low)
                self._close = push_back_data(self._close, close)
                self._volume = push_back_data(self._volume, volume)

            self._next_data_list.clear()
            self._next_wall += self._interval

        self._next_data_list.append([tick_date, float(data.price), float(data.volume)])

    def run(self):
        df = calc_features(self.df)
        pred = self._estimator.predict(df.select(self.train_features).to_numpy()[-1:])
        # 予測が正の場合は買い注文
        if pred > 0:
            row = df[-1]
            price = row["close"][0] - row["ATR"][0] * 0.5
            volume = self._wallet.get_current_total_assets({self._symbol: row["close"][0]})
            volume = self._wallet.calc_trade_volume(
                self._symbol, price, volume, self._trader.fee_rate(self._symbol)
            )
            deadline = self._next_wall + self._interval
            history = self._trader.buy_order(self._symbol, price, volume, deadline=deadline)
            self._wallet.update_wallet(history)
