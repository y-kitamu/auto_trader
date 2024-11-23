"""history.py
"""

from pathlib import Path

import polars as pl

from ..order import BaseOrder


def log_closed_order(closed_orders: list[BaseOrder], trade_history_csv: Path):
    """closed_ordersの情報をcsvに書き込む"""
    if not closed_orders:
        return

    df = pl.from_dicts(sum([order.summary() for order in closed_orders], []))
    if not trade_history_csv.exists():
        df.write_csv(trade_history_csv)
    else:
        with open(trade_history_csv, "a") as f:
            df.write_csv(f, include_header=False)
