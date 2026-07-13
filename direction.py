from indicators import (
    calc_rsi, calc_vwap, calc_bollinger_bands, calc_kline_momentum, calc_ema,
    calc_macd, calc_obv_trend, calc_volume_ratio,
)


def score_direction(klines: list, price: float) -> int:
    """综合评分：各指标一致性越多，方向越可靠。满分为 ±12 分。"""
    if len(klines) < 14:
        return 0

    rsi = calc_rsi(klines)
    vwap = calc_vwap(klines)
    bb = calc_bollinger_bands(klines)
    momentum = calc_kline_momentum(klines)
    ema_short = calc_ema(klines, 12)
    ema_long = calc_ema(klines, 26)
    macd = calc_macd(klines)
    obv_trend = calc_obv_trend(klines)
    vol_ratio = calc_volume_ratio(klines)

    score = 0

    # === RSI ===
    if rsi < 30:
        score += 2
    elif rsi < 40:
        score += 1
    elif rsi > 70:
        score -= 2
    elif rsi > 60:
        score -= 1

    # === VWAP 均线 ===
    if vwap > 0:
        if price > vwap:
            score += 1
        else:
            score -= 1

    # === 布林带位置 ===
    if bb["middle"] > 0:
        if price > bb["upper"]:
            score -= 2
        elif price > bb["middle"]:
            score += 1
        elif price < bb["lower"]:
            score += 2
        elif price < bb["middle"]:
            score -= 1

    # === 动量 ===
    if momentum > 1.0:
        score += 2
    elif momentum > 0.5:
        score += 1
    elif momentum < -1.0:
        score -= 2
    elif momentum < -0.5:
        score -= 1

    # === EMA 金叉/死叉 ===
    if ema_short > 0 and ema_long > 0:
        if ema_short > ema_long:
            score += 1
        else:
            score -= 1

    # === MACD 金叉/死叉 ===
    if macd["cross"] == "golden":
        score += 2
    elif macd["cross"] == "death":
        score -= 2

    # === OBV 趋势 ===
    if obv_trend == "bullish":
        score += 1
    elif obv_trend == "bearish":
        score -= 1

    # === 成交量放大 ===
    if vol_ratio > 2.0:
        # 放量，配合方向信号确认
        if score > 0:
            score += 1
        elif score < 0:
            score -= 1
    elif vol_ratio < 0.5:
        # 缩量，减弱信号
        pass  # 不加分不减分

    return score


def interpret(score: int) -> str:
    if score >= 5:
        return "bullish"
    elif score >= 3:
        return "bullish_weak"
    elif score <= -5:
        return "bearish"
    elif score <= -3:
        return "bearish_weak"
    else:
        return "neutral"


def get_direction_confidence(score: int, direction: str) -> float:
    """
    置信度：基于指标一致性强弱。
    neutral 固定 74%（没有方向信号时不操作）。
    有方向时，分数绝对值越大置信度越高，最高约 85%。
    """
    if direction == "neutral":
        return 0.74

    # 分数映射到置信度：|score|=3 → 0.60, |score|>=8 → 0.85
    normalized = min(abs(score) - 2, 6) / 6.0  # 0.0 ~ 1.0
    confidence = 0.60 + normalized * 0.25
    return round(confidence, 2)


def get_direction_description(direction: str) -> str:
    descriptions = {
        "bullish": "强烈看多（多指标共振）",
        "bullish_weak": "温和看多（部分指标支持）",
        "bearish": "强烈看空（多指标共振）",
        "bearish_weak": "温和看空（部分指标支持）",
        "neutral": "中性（指标分歧，无明确方向）",
    }
    return descriptions.get(direction, "未知")
