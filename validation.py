import csv
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

HISTORY_FILE = os.getenv("HISTORY_FILE", "history.csv")


def check_and_verify_last(actual_price: float) -> dict:
    if not os.path.exists(HISTORY_FILE):
        return {"verified": False, "message": "无历史记录"}

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return {"verified": False, "message": "历史记录为空"}

    last_row = rows[-1]

    try:
        predicted_lower = float(last_row["predicted_lower"])
        predicted_upper = float(last_row["predicted_upper"])
        predicted_direction = last_row["direction"]
        predicted_time = last_row["timestamp"]
    except (KeyError, ValueError):
        return {"verified": False, "message": "历史记录格式错误"}

    in_range = predicted_lower <= actual_price <= predicted_upper

    direction_correct = False
    if predicted_direction == "neutral":
        direction_correct = in_range
    elif predicted_direction in ("bullish", "bullish_weak"):
        direction_correct = actual_price >= float(last_row["price"])
    elif predicted_direction in ("bearish", "bearish_weak"):
        direction_correct = actual_price <= float(last_row["price"])

    return {
        "verified": True,
        "in_range": in_range,
        "direction_correct": direction_correct,
        "predicted_lower": predicted_lower,
        "predicted_upper": predicted_upper,
        "predicted_direction": predicted_direction,
        "predicted_price": float(last_row["price"]),
        "actual_price": actual_price,
        "predicted_time": predicted_time,
        "message": f"预测区间验证: {'✓' if in_range else '✗'} | 方向验证: {'✓' if direction_correct else '✗'}",
    }


def analyze_rules(lookback_days: int = 7) -> dict:
    if not os.path.exists(HISTORY_FILE):
        return {"error": "无历史记录"}

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return {"error": "历史记录为空"}

    cutoff_time = (datetime.now() - timedelta(days=lookback_days)).timestamp()

    recent_rows = []
    for row in rows:
        try:
            ts = float(row["timestamp"])
            if ts >= cutoff_time:
                recent_rows.append(row)
        except (KeyError, ValueError):
            continue

    if not recent_rows:
        return {"error": "最近无有效记录"}

    direction_stats = {}
    for row in recent_rows:
        direction = row.get("direction", "unknown")
        if direction not in direction_stats:
            direction_stats[direction] = {"total": 0, "correct": 0}
        direction_stats[direction]["total"] += 1

        actual_price = float(row.get("actual_price", 0))
        predicted_lower = float(row.get("predicted_lower", 0))
        predicted_upper = float(row.get("predicted_upper", 0))
        predicted_price = float(row.get("price", 0))

        in_range = predicted_lower <= actual_price <= predicted_upper

        if direction == "neutral":
            correct = in_range
        elif direction in ("bullish", "bullish_weak"):
            correct = actual_price >= predicted_price
        elif direction in ("bearish", "bearish_weak"):
            correct = actual_price <= predicted_price
        else:
            correct = False

        if correct:
            direction_stats[direction]["correct"] += 1

    results = {}
    for direction, stats in direction_stats.items():
        accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        results[direction] = {
            "total": stats["total"],
            "correct": stats["correct"],
            "accuracy": round(accuracy * 100, 1),
        }

    total_predictions = len(recent_rows)
    range_correct = sum(1 for row in recent_rows if float(row.get("actual_price", 0)) > 0 and
                        float(row.get("predicted_lower", 0)) <= float(row.get("actual_price", 0)) <= float(row.get("predicted_upper", 0)))

    return {
        "lookback_days": lookback_days,
        "total_predictions": total_predictions,
        "range_accuracy": round(range_correct / total_predictions * 100, 1) if total_predictions > 0 else 0,
        "direction_stats": results,
    }