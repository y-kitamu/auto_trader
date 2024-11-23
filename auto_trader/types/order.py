"""order.py
"""

from pydantic import BaseModel


class Order(BaseModel):
    order_id: str
    symbol: str
    price: float
    fee: float
    volume: float  # positive value:  buy, negative value: sell
