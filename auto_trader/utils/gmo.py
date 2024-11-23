"""gmo.py
"""

import datetime
import hashlib
import hmac
import json
import time

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


def public_api(path: str, parameters: dict):
    path += "?{}".format("&".join([f"{k}={v}" for k, v in parameters.items()]))
    res = requests.get(PUBLIC_END_POINT + path)
    if res["status"] != 0:
        raise RuntimeError(
            "Failed to run GMO API. Response : {}".format(json.dumps(res.json(), indent=2))
        )
    return res.json()


def private_api(path: str, parameters: dict, method: str):
    timestamp = "{0}000".format(int(time.mktime(datetime.datetime.now().timetuple())))

    with open(CERT_FILE, "r") as f:
        cert = json.load(f)
        api_key = cert["api_key"]
        secret_key = cert["api_secret"]

    text = timestamp + method + path
    if method != "GET":
        text += json.dumps(parameters)
    sign = hmac.new(
        bytes(secret_key.encode("ascii")), bytes(text.encode("ascii")), hashlib.sha256
    ).hexdigest()

    headers = {"API-KEY": api_key, "API-TIMESTAMP": timestamp, "API-SIGN": sign}

    if method == "GET":
        res = requests.get(PRIVATE_END_POINT + path, headers=headers, params=parameters)
    elif method == "POST":
        res = requests.post(PRIVATE_END_POINT + path, headers=headers, data=json.dumps(parameters))
    elif method == "PUT":
        res = requests.put(PRIVATE_END_POINT + path, headers=headers, data=json.dumps(parameters))
    else:
        raise ValueError(f"Invalid method: {method}")

    if res["status"] != 0:
        raise RuntimeError(
            "Failed to run GMO API. Response : {}".format(json.dumps(res.json(), indent=2))
        )

    return res.json()


def get_ohlc(symbol, interval: str | datetime.timedelta, date=datetime.datetime.now()) -> pl.DataFrame:
    if isinstance(interval, datetime.timedelta):
        interval = convert_timedelta_to_str(interval)
    date_str = date.strftime("%Y%m%d")
    path = f"/v1/klines?symbol={symbol}&interval={interval}&date={date_str}"

    response = requests.get(PUBLIC_END_POINT + path)
    res = response.json()
    if res["status"] != 0:
        raise RuntimeError("Failed to run GMO API. Response : {}".format(json.dumps(res, indent=2)))
    if "data" not in res or len(res["data"]) == 0:
        logger.warning(f"No data for {symbol} on {date}")
        return pl.DataFrame()

    df = (
        pl.from_dicts(res["data"])
        .with_columns(
            pl.col("openTime").cast(pl.Float64),
            pl.col("open").cast(pl.Float64),
            pl.col("high").cast(pl.Float64),
            pl.col("low").cast(pl.Float64),
            pl.col("close").cast(pl.Float64),
            pl.col("volume").cast(pl.Float64),
        )
        .with_columns(
            (pl.from_epoch("openTime", time_unit="ms") + pl.duration(hours=9)).alias("datetime"),  # JST
        )
    )
    return df
