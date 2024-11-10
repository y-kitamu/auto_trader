"""feature.py
"""

import polars as pl
import talib


def calc_features(df: pl.DataFrame):

    open_ = df["open"].to_numpy()
    high = df["high"].to_numpy()
    low = df["low"].to_numpy()
    close = df["close"].to_numpy()
    volume = df["volume"].to_numpy()

    hilo = (high + low) / 2
    # 価格(hilo または close)を引いた後、価格(close)で割ることで標準化
    BBANDS_upperband, BBANDS_middleband, BBANDS_lowerband = talib.BBANDS(
        close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0
    )
    BBANDS_upperband = (BBANDS_upperband - hilo) / close
    BBANDS_middleband = (BBANDS_middleband - hilo) / close
    BBANDS_lowerband = (BBANDS_lowerband - hilo) / close
    DEMA = (talib.DEMA(close, timeperiod=30) - hilo) / close
    EMA = (talib.EMA(close, timeperiod=30) - hilo) / close
    HT_TRENDLINE = (talib.HT_TRENDLINE(close) - hilo) / close
    KAMA = (talib.KAMA(close, timeperiod=30) - hilo) / close
    MA = (talib.MA(close, timeperiod=30, matype=0) - hilo) / close
    MIDPOINT = (talib.MIDPOINT(close, timeperiod=14) - hilo) / close
    SMA = (talib.SMA(close, timeperiod=30) - hilo) / close
    T3 = (talib.T3(close, timeperiod=5, vfactor=0) - hilo) / close
    TEMA = (talib.TEMA(close, timeperiod=30) - hilo) / close
    TRIMA = (talib.TRIMA(close, timeperiod=30) - hilo) / close
    WMA = (talib.WMA(close, timeperiod=30) - hilo) / close
    LINEARREG = (talib.LINEARREG(close, timeperiod=14) - close) / close
    LINEARREG_INTERCEPT = (talib.LINEARREG_INTERCEPT(close, timeperiod=14) - close) / close

    # 価格(close)で割ることで標準化
    AD = talib.AD(high, low, close, volume) / close
    ADOSC = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10) / close
    APO = talib.APO(close, fastperiod=12, slowperiod=26, matype=0) / close
    HT_PHASOR_inphase, HT_PHASOR_quadrature = talib.HT_PHASOR(close)
    HT_PHASOR_inphase /= close
    HT_PHASOR_quadrature /= close
    LINEARREG_SLOPE = talib.LINEARREG_SLOPE(close, timeperiod=14) / close
    MACD_macd, MACD_macdsignal, MACD_macdhist = talib.MACD(
        close, fastperiod=12, slowperiod=26, signalperiod=9
    )
    MACD_macd /= close
    MACD_macdsignal /= close
    MACD_macdhist /= close
    MINUS_DM = talib.MINUS_DM(high, low, timeperiod=14) / close
    MOM = talib.MOM(close, timeperiod=10) / close
    OBV = talib.OBV(close, volume) / close
    PLUS_DM = talib.PLUS_DM(high, low, timeperiod=14) / close
    STDDEV = talib.STDDEV(close, timeperiod=5, nbdev=1) / close
    TRANGE = talib.TRANGE(high, low, close) / close

    ADX = talib.ADX(high, low, close, timeperiod=14)
    ADXR = talib.ADXR(high, low, close, timeperiod=14)
    AROON_aroondown, AROON_aroonup = talib.AROON(high, low, timeperiod=14)
    AROONOSC = talib.AROONOSC(high, low, timeperiod=14)
    BOP = talib.BOP(open_, high, low, close)
    CCI = talib.CCI(high, low, close, timeperiod=14)
    DX = talib.DX(high, low, close, timeperiod=14)
    # skip MACDEXT MACDFIX たぶん同じなので
    MFI = talib.MFI(high, low, close, volume, timeperiod=14)
    MINUS_DI = talib.MINUS_DI(high, low, close, timeperiod=14)
    PLUS_DI = talib.PLUS_DI(high, low, close, timeperiod=14)
    RSI = talib.RSI(close, timeperiod=14)
    STOCH_slowk, STOCH_slowd = talib.STOCH(
        high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0
    )
    STOCHF_fastk, STOCHF_fastd = talib.STOCHF(
        high, low, close, fastk_period=5, fastd_period=3, fastd_matype=0
    )
    STOCHRSI_fastk, STOCHRSI_fastd = talib.STOCHRSI(
        close, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0
    )
    TRIX = talib.TRIX(close, timeperiod=30)
    ULTOSC = talib.ULTOSC(high, low, close, timeperiod1=7, timeperiod2=14, timeperiod3=28)
    WILLR = talib.WILLR(high, low, close, timeperiod=14)

    ATR = talib.ATR(high, low, close, timeperiod=14)
    NATR = talib.NATR(high, low, close, timeperiod=14)

    HT_DCPERIOD = talib.HT_DCPERIOD(close)
    HT_DCPHASE = talib.HT_DCPHASE(close)
    HT_SINE_sine, HT_SINE_leadsine = talib.HT_SINE(close)
    HT_TRENDMODE = talib.HT_TRENDMODE(close)

    BETA = talib.BETA(high, low, timeperiod=5)
    CORREL = talib.CORREL(high, low, timeperiod=30)

    LINEARREG_ANGLE = talib.LINEARREG_ANGLE(close, timeperiod=14)

    df = df.with_columns(
        pl.Series(BBANDS_upperband).alias("BBANDS_upperband"),
        pl.Series(BBANDS_middleband).alias("BBANDS_middleband"),
        pl.Series(BBANDS_lowerband).alias("BBANDS_lowerband"),
        pl.Series(DEMA).alias("DEMA"),
        pl.Series(EMA).alias("EMA"),
        pl.Series(HT_TRENDLINE).alias("HT_TRENDLINE"),
        pl.Series(KAMA).alias("KAMA"),
        pl.Series(MA).alias("MA"),
        pl.Series(MIDPOINT).alias("MIDPOINT"),
        pl.Series(SMA).alias("SMA"),
        pl.Series(T3).alias("T3"),
        pl.Series(TEMA).alias("TEMA"),
        pl.Series(TRIMA).alias("TRIMA"),
        pl.Series(WMA).alias("WMA"),
        pl.Series(LINEARREG).alias("LINEARREG"),
        pl.Series(LINEARREG_INTERCEPT).alias("LINEARREG_INTERCEPT"),
        pl.Series(AD).alias("AD"),
        pl.Series(ADOSC).alias("ADOSC"),
        pl.Series(APO).alias("APO"),
        pl.Series(HT_PHASOR_inphase).alias("HT_PHASOR_inphase"),
        pl.Series(HT_PHASOR_quadrature).alias("HT_PHASOR_quadrature"),
        pl.Series(LINEARREG_SLOPE).alias("LINEARREG_SLOPE"),
        pl.Series(MACD_macd).alias("MACD_macd"),
        pl.Series(MACD_macdsignal).alias("MACD_macdsignal"),
        pl.Series(MACD_macdhist).alias("MACD_macdhist"),
        pl.Series(MINUS_DM).alias("MINUS_DM"),
        pl.Series(MOM).alias("MOM"),
        pl.Series(OBV).alias("OBV"),
        pl.Series(PLUS_DM).alias("PLUS_DM"),
        pl.Series(STDDEV).alias("STDDEV"),
        pl.Series(TRANGE).alias("TRANGE"),
        pl.Series(ADX).alias("ADX"),
        pl.Series(ADXR).alias("ADXR"),
        pl.Series(AROON_aroondown).alias("AROON_aroondown"),
        pl.Series(AROON_aroonup).alias("AROON_aroonup"),
        pl.Series(AROONOSC).alias("AROONOSC"),
        pl.Series(BOP).alias("BOP"),
        pl.Series(CCI).alias("CCI"),
        pl.Series(DX).alias("DX"),
        pl.Series(MFI).alias("MFI"),
        pl.Series(MINUS_DI).alias("MINUS_DI"),
        pl.Series(PLUS_DI).alias("PLUS_DI"),
        pl.Series(RSI).alias("RSI"),
        pl.Series(STOCH_slowk).alias("STOCH_slowk"),
        pl.Series(STOCH_slowd).alias("STOCH_slowd"),
        pl.Series(STOCHF_fastk).alias("STOCHF_fastk"),
        pl.Series(STOCHF_fastd).alias("STOCHF_fastd"),
        pl.Series(STOCHRSI_fastk).alias("STOCHRSI_fastk"),
        pl.Series(STOCHRSI_fastd).alias("STOCHRSI_fastd"),
        pl.Series(TRIX).alias("TRIX"),
        pl.Series(ULTOSC).alias("ULTOSC"),
        pl.Series(WILLR).alias("WILLR"),
        pl.Series(ATR).alias("ATR"),
        pl.Series(NATR).alias("NATR"),
        pl.Series(HT_DCPERIOD).alias("HT_DCPERIOD"),
        pl.Series(HT_DCPHASE).alias("HT_DCPHASE"),
        pl.Series(HT_SINE_sine).alias("HT_SINE_sine"),
        pl.Series(HT_SINE_leadsine).alias("HT_SINE_leadsine"),
        pl.Series(HT_TRENDMODE).alias("HT_TRENDMODE"),
        pl.Series(BETA).alias("BETA"),
        pl.Series(CORREL).alias("CORREL"),
        pl.Series(LINEARREG_ANGLE).alias("LINEARREG_ANGLE"),
    )
    return df
