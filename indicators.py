import math


def calc_ema(klines: list, period: int = 12) -> float:
    if len(klines) < period:
        return 0.0
    closes = [k["close"] for k in klines]
    multiplier = 2.0 / (period + 1)
    ema = sum(closes[-period:]) / period
    for price in closes[-period + 1 :]:
        ema = (price - ema) * multiplier + ema
    return ema


def calc_rsi(klines: list, period: int = 14) -> float:
    if len(klines) < period + 1:
        return 50.0
    deltas = []
    for i in range(1, len(klines)):
        deltas.append(klines[i]["close"] - klines[i - 1]["close"])
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calc_vwap(klines: list) -> float:
    if not klines:
        return 0.0
    cumulative_price_volume = 0.0
    cumulative_volume = 0.0
    for kline in klines:
        tp = (kline["high"] + kline["low"] + kline["close"]) / 3
        cumulative_price_volume += tp * kline["volume"]
        cumulative_volume += kline["volume"]
    if cumulative_volume == 0:
        return 0.0
    return cumulative_price_volume / cumulative_volume


def calc_bollinger_bands(klines: list, period: int = 20, num_std: float = 2.0) -> dict:
    if len(klines) < period:
        return {"middle": 0, "upper": 0, "lower": 0}
    closes = [k["close"] for k in klines[-period:]]
    middle = sum(closes) / period
    variance = sum((c - middle) ** 2 for c in closes) / period
    std_dev = math.sqrt(variance)
    return {
        "middle": middle,
        "upper": middle + num_std * std_dev,
        "lower": middle - num_std * std_dev,
    }


def calc_atr(klines: list, period: int = 14) -> float:
    if len(klines) < period + 1:
        return 0.0
    tr_values = []
    for i in range(1, len(klines)):
        high = klines[i]["high"]
        low = klines[i]["low"]
        prev_close = klines[i - 1]["close"]
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        tr_values.append(max(tr1, tr2, tr3))
    atr = sum(tr_values[-period:]) / period
    return atr


def calc_atr_percentile(klines: list, period: int = 14, lookback: int = 100) -> float:
    if len(klines) < lookback + period:
        return 50.0
    atr_values = []
    for i in range(lookback):
        sub_klines = klines[i : i + period + 1]
        atr = calc_atr(sub_klines, period)
        if atr > 0:
            atr_values.append(atr)
    if not atr_values:
        return 50.0
    current_atr = calc_atr(klines[-period - 1 :], period)
    if current_atr <= 0:
        return 50.0
    count_below = sum(1 for a in atr_values if a <= current_atr)
    return (count_below / len(atr_values)) * 100


def calc_kline_momentum(klines: list, lookback: int = 4) -> float:
    if len(klines) < lookback:
        return 0.0
    recent = klines[-lookback:]
    momentum = 0.0
    for i in range(1, len(recent)):
        momentum += recent[i]["close"] - recent[i - 1]["close"]
    if recent[-1]["close"] > 0:
        return (momentum / recent[-1]["close"]) * 100
    return 0.0


def calc_macd(klines: list, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """MACD 指标：返回 macd线, signal线, histogram"""
    if len(klines) < slow + signal:
        return {"macd": 0, "signal": 0, "histogram": 0, "cross": "none"}

    closes = [k["close"] for k in klines]

    def ema(data: list, period: int) -> float:
        if len(data) < period:
            return sum(data) / len(data) if data else 0
        multiplier = 2.0 / (period + 1)
        ema_val = sum(data[-period:]) / period
        for price in data[-period + 1:]:
            ema_val = (price - ema_val) * multiplier + ema_val
        return ema_val

    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    macd_line = ema_fast - ema_slow

    # Signal line (EMA of MACD)
    macd_values = []
    for i in range(slow - 1, len(closes)):
        ef = ema(closes[:i + 1], fast)
        es = ema(closes[:i + 1], slow)
        macd_values.append(ef - es)
    if len(macd_values) < signal:
        signal_line = macd_line
    else:
        signal_line = ema(macd_values, signal)

    histogram = macd_line - signal_line

    # 金叉/死叉判断（前一根 histogram）
    if len(macd_values) >= signal:
        prev_hist = macd_values[-2] if len(macd_values) >= 2 else 0
        if prev_hist < 0 <= histogram:
            cross = "golden"  # 金叉
        elif prev_hist > 0 >= histogram:
            cross = "death"   # 死叉
        else:
            cross = "none"
    else:
        cross = "none"

    return {
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram,
        "cross": cross,
    }


def calc_obv(klines: list) -> float:
    """OBV 能量潮：累计成交量配合价格"""
    if len(klines) < 2:
        return 0.0
    obv = 0.0
    for i in range(1, len(klines)):
        if klines[i]["close"] > klines[i - 1]["close"]:
            obv += klines[i]["volume"]
        elif klines[i]["close"] < klines[i - 1]["close"]:
            obv -= klines[i]["volume"]
    return obv


def calc_obv_trend(klines: list, period: int = 20) -> str:
    """OBV 趋势方向"""
    if len(klines) < period + 1:
        return "neutral"
    recent = klines[-period:]
    first_half = sum(klines[i]["volume"] for i in range(period // 2)
                     if recent[i]["close"] >= recent[i - 1]["close"]) - \
           sum(klines[i]["volume"] for i in range(period // 2)
                     if recent[i]["close"] < recent[i - 1]["close"])
    second_half = sum(klines[i]["volume"] for i in range(period // 2, period - 1)
                       if recent[i]["close"] >= recent[i - 1]["close"]) - \
           sum(klines[i]["volume"] for i in range(period // 2, period - 1)
                       if recent[i]["close"] < recent[i - 1]["close"])
    if second_half > first_half * 1.2:
        return "bullish"
    elif second_half < first_half * 0.8:
        return "bearish"
    return "neutral"


def calc_volume_ratio(klines: list, period: int = 20) -> float:
    """成交量放大比：当前成交量 / 过去 N 根平均成交量"""
    if len(klines) < period + 1:
        return 1.0
    recent_vols = [klines[i]["volume"] for i in range(-period, -1)]
    avg_vol = sum(recent_vols) / len(recent_vols)
    current_vol = klines[-1]["volume"]
    if avg_vol <= 0:
        return 1.0
    return current_vol / avg_vol


def calc_support_resistance(daily_klines: list) -> dict:
    if len(daily_klines) < 5:
        return {"support": 0, "resistance": 0}
    lows = [k["low"] for k in daily_klines]
    highs = [k["high"] for k in daily_klines]
    support = sum(lows[-5:]) / 5
    resistance = sum(highs[-5:]) / 5
    return {"support": support, "resistance": resistance}