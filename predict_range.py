from indicators import calc_atr, calc_atr_percentile, calc_bollinger_bands


def predict_range(price: float, klines: list) -> dict:
    if len(klines) < 14 or price <= 0:
        return {
            "width": "normal",
            "lower": price * 0.996,
            "upper": price * 1.004,
            "range_pct": 0.8,
        }

    atr = calc_atr(klines)
    atr_percentile = calc_atr_percentile(klines)
    bb = calc_bollinger_bands(klines)

    if atr > 0:
        atr_pct = (atr / price) * 100
    else:
        atr_pct = 0.5

    width = "normal"
    range_pct = 0.8

    if atr_percentile > 70:
        if atr_pct > 1.2:
            width = "loose"
            range_pct = 1.5
        else:
            width = "normal"
            range_pct = 1.0
    elif atr_percentile < 30:
        width = "tight"
        range_pct = 0.4
    else:
        if atr_pct < 0.3:
            width = "tight"
            range_pct = 0.4
        elif atr_pct < 0.6:
            width = "normal"
            range_pct = 0.6
        else:
            width = "normal"
            range_pct = 0.8

    half_range = range_pct / 2
    lower = price * (1 - half_range / 100)
    upper = price * (1 + half_range / 100)

    if bb["middle"] > 0:
        if lower < bb["lower"]:
            lower = bb["lower"] * 0.998
        if upper > bb["upper"]:
            upper = bb["upper"] * 1.002

    return {
        "width": width,
        "lower": lower,
        "upper": upper,
        "range_pct": range_pct,
        "atr_pct": atr_pct,
        "atr_percentile": atr_percentile,
    }


def get_range_width_description(width: str) -> str:
    descriptions = {
        "tight": "窄区间（±0.4%）",
        "normal": "正常区间（±0.4~0.8%）",
        "loose": "宽区间（±0.8%以上）",
    }
    return descriptions.get(width, "未知")