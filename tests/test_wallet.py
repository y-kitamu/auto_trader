"""test_wallet.py
"""

import datetime

import auto_trader


def test_wallet():
    initial_cash = 100000
    wallet = auto_trader.wallet.Wallet(initial_cash=initial_cash)
    assert wallet.get_current_total_assets({}) == initial_cash

    # トレード可能量の計算
    tradable_volume = wallet.calc_trade_volume("BTC_JPY", 30000, 3.0, 0.001)
    assert abs(tradable_volume - 3.0) < 1e-6
    tradable_volume = wallet.calc_trade_volume("BTC_JPY", 30000, 3.0, 1.0)
    assert abs(tradable_volume - 0.0) < 1e-6

    # ポジションの取得(新規)
    position = wallet.get_target_position("BTC_JPY")
    assert position.volume == 0

    # ポジションの更新
    trade_history = auto_trader.types.TradeHistory(
        symbol="BTC_JPY", volume=3.0, price=30000, fee=0.001, timestamp=datetime.datetime.now()
    )
    wallet.update_wallet(trade_history)

    # 総資産の計算
    fee = trade_history.volume * trade_history.price * trade_history.fee
    asset = wallet.get_current_total_assets({"BTC_JPY": 30000})
    assert abs(asset - (initial_cash - fee)) < 1e-6
    asset = wallet.get_current_total_assets({"BTC_JPY": 20000})
    assert abs(asset - (70000 - fee)) < 1e-6

    # ポジションの更新
    trade_history = auto_trader.types.TradeHistory(
        symbol="BTC_JPY", volume=-1.0, price=35000, fee=0.001, timestamp=datetime.datetime.now()
    )
    wallet.update_wallet(trade_history)

    # 総資産の計算
    fee += abs(trade_history.volume) * trade_history.price * trade_history.fee
    asset = wallet.get_current_total_assets({"BTC_JPY": 20000})
    assert abs(asset - (10000 + 35000 * 1.0 + 20000 * 2.0 - fee)) < 1e-6

    # トレード可能量の計算
    tradable_volume = wallet.calc_trade_volume("BTC_JPY", 20000, -8.0, 0.001)
    assert abs(tradable_volume + 4.0) < 1e-6
