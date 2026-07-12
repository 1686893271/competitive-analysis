import csv
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

HISTORY_FILE = os.getenv("HISTORY_FILE", "history.csv")

FIELDNAMES = [
    "timestamp",
    "datetime",
    "coin_type",
    "price",
    "direction",
    "direction_score",
    "confidence",
    "predicted_lower",
    "predicted_upper",
    "range_width",
    "range_pct",
    "market_regime",
    "source",
    "percent_change_24h",
    "actual_price",
]


def init_history_file():
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def write_prediction(coin_type: str, price: float, direction: str, direction_score: int,
                      confidence: float, range_data: dict, regime: str, source: str,
                      percent_change_24h: float):
    init_history_file()

    now = datetime.now()
    timestamp = now.timestamp()

    record = {
        "timestamp": timestamp,
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "coin_type": coin_type,
        "price": price,
        "direction": direction,
        "direction_score": direction_score,
        "confidence": confidence,
        "predicted_lower": range_data["lower"],
        "predicted_upper": range_data["upper"],
        "range_width": range_data["width"],
        "range_pct": range_data["range_pct"],
        "market_regime": regime,
        "source": source,
        "percent_change_24h": percent_change_24h,
        "actual_price": "",
    }

    with open(HISTORY_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(record)

    print(f"预测记录已写入: {now.strftime('%Y-%m-%d %H:%M:%S')}")


def update_last_actual_price(actual_price: float):
    """已废弃 - actual_price 由下一小时验证时自动填充"""
    pass


def get_last_prediction(coin_type: str = None) -> dict:
    if not os.path.exists(HISTORY_FILE):
        return {}

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return {}

    if coin_type:
        for row in reversed(rows):
            if row.get("coin_type") == coin_type:
                return row
        return {}

    return rows[-1]