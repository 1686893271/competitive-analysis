from indicators import calc_rsi, calc_atr_percentile, calc_bollinger_bands, calc_kline_momentum


def detect_market_regime(klines: list) -> str:
    if len(klines) < 24:
        return "neutral"

    rsi = calc_rsi(klines)
    atr_percentile = calc_atr_percentile(klines)
    bb = calc_bollinger_bands(klines)
    momentum = calc_kline_momentum(klines)
    last_close = klines[-1]["close"]

    volatility_score = 0
    if atr_percentile > 70:
        volatility_score = 2
    elif atr_percentile > 40:
        volatility_score = 1
    else:
        volatility_score = 0

    trend_score = 0
    if momentum > 0.5:
        trend_score = 1
    elif momentum < -0.5:
        trend_score = -1

    position_score = 0
    if bb["middle"] > 0:
        if last_close > bb["upper"]:
            position_score = 2
        elif last_close > bb["middle"]:
            position_score = 1
        elif last_close < bb["lower"]:
            position_score = -2
        elif last_close < bb["middle"]:
            position_score = -1

    if volatility_score == 2:
        if rsi > 70:
            return "high_vol_bearish"
        elif rsi < 30:
            return "high_vol_bullish"
        return "high_vol"

    if volatility_score == 0:
        if trend_score == 1 and position_score >= 1:
            return "low_vol_uptrend"
        elif trend_score == -1 and position_score <= -1:
            return "low_vol_downtrend"
        return "low_vol_range"

    if trend_score == 1 and position_score >= 1:
        return "normal_uptrend"
    elif trend_score == -1 and position_score <= -1:
        return "normal_downtrend"

    return "neutral"


def get_regime_description(regime: str) -> str:
    descriptions = {
        "high_vol_bearish": "高波动 + 超买 → 警惕回调",
        "high_vol_bullish": "高波动 + 超卖 → 可能反弹",
        "high_vol": "高波动状态 → 谨慎操作",
        "low_vol_uptrend": "低波动上涨 → 趋势稳定",
        "low_vol_downtrend": "低波动下跌 → 趋势稳定",
        "low_vol_range": "低波动震荡 → 区间操作",
        "normal_uptrend": "正常波动上涨 → 趋势健康",
        "normal_downtrend": "正常波动下跌 → 趋势健康",
        "neutral": "中性状态 → 观望为主",
    }
    return descriptions.get(regime, "未知状态")