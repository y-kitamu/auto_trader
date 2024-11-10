"""gmo.py
"""

import datetime

import polars as pl
import requests

from ..constants import PROJECT_ROOT
from ..logging import logger

CERT_FILE = PROJECT_ROOT / "cert" / "gmo_api.json"

PUBLIC_END_POINT = "https://api.coin.z.com/public"
PRIVATE_END_POINT = "https://api.coin.z.com/private"


def convert_timedelta_to_str(interval: datetime.timedelta):
    """timedeltaをgmoのAPIで使う文字列に変換する"""
    if interval == datetime.timedelta(minutes=1):
        return "1min"
    if interval == datetime.timedelta(minutes=5):
        return "5min"
    if interval == datetime.timedelta(minutes=10):
        return "10min"
    if interval == datetime.timedelta(minutes=15):
        return "15min"
    if interval == datetime.timedelta(minutes=30):
        return "30min"
    if interval == datetime.timedelta(hours=1):
        return "1hour"
    if interval == datetime.timedelta(hours=4):
        return "4hour"
    if interval == datetime.timedelta(hours=8):
        return "8hour"
    if interval == datetime.timedelta(hours=12):
        return "12hour"
    if interval == datetime.timedelta(days=1):
        return "1day"
    if interval == datetime.timedelta(weeks=1):
        return "1week"
    if interval == datetime.timedelta(days=30):
        return "1month"
    raise ValueError(f"Invalid interval: {interval}")


def get_ohlc(symbol, interval: str | datetime.timedelta, date=datetime.datetime.now()) -> pl.DataFrame:
    if isinstance(interval, datetime.timedelta):
        interval = convert_timedelta_to_str(interval)
    date_str = date.strftime("%Y%m%d")
    path = f"/v1/klines?symbol={symbol}&interval={interval}&date={date_str}"

    response = requests.get(PUBLIC_END_POINT + path)
    res = response.json()
    if "data" not in res or len(res["data"]) == 0:
        logger.warning(f"No data for {symbol} on {date}")
        return pl.DataFrame()

    df = (
        pl.from_dicts(res["data"])
        .with_columns(
            pl.col("openTime").cast(pl.Float64),
            pl.col("open").cast(pl.Int64),
            pl.col("high").cast(pl.Int64),
            pl.col("low").cast(pl.Int64),
            pl.col("close").cast(pl.Int64),
            pl.col("volume").cast(pl.Float64),
        )
        .with_columns(
            (pl.from_epoch("openTime", time_unit="ms") + pl.duration(hours=9)).alias("datetime"),  # JST
        )
    )
    return df
