from indicators import calc_rsi, calc_vwap, calc_bollinger_bands, calc_kline_momentum, calc_ema


def score_direction(klines: list, price: float) -> int:
    if len(klines) < 14:
        return 0

    rsi = calc_rsi(klines)
    vwap = calc_vwap(klines)
    bb = calc_bollinger_bands(klines)
    momentum = calc_kline_momentum(klines)
    ema_short = calc_ema(klines, 12)
    ema_long = calc_ema(klines, 26)

    score = 0

    if rsi < 30:
        score += 2
    elif rsi < 40:
        score += 1
    elif rsi > 70:
        score -= 2
    elif rsi > 60:
        score -= 1

    if vwap > 0:
        if price > vwap:
            score += 1
        else:
            score -= 1

    if bb["middle"] > 0:
        if price > bb["upper"]:
            score -= 2
        elif price > bb["middle"]:
            score += 1
        elif price < bb["lower"]:
            score += 2
        elif price < bb["middle"]:
            score -= 1

    if momentum > 1.0:
        score += 2
    elif momentum > 0.5:
        score += 1
    elif momentum < -1.0:
        score -= 2
    elif momentum < -0.5:
        score -= 1

    if ema_short > 0 and ema_long > 0:
        if ema_short > ema_long:
            score += 1
        else:
            score -= 1

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
    if direction == "neutral":
        return 0.74
    elif direction == "bullish":
        return 0.05 + (score - 5) * 0.01
    elif direction == "bullish_weak":
        return 0.05
    elif direction == "bearish":
        return 0.08 + (-score - 5) * 0.01
    elif direction == "bearish_weak":
        return 0.08
    return 0.5


def get_direction_description(direction: str) -> str:
    descriptions = {
        "bullish": "强烈看多",
        "bullish_weak": "温和看多",
        "bearish": "强烈看空",
        "bearish_weak": "温和看空",
        "neutral": "中性（82%概率随机游走）",
    }
    return descriptions.get(direction, "未知")