#!/usr/bin/env python3
# coding: utf-8

import argparse
import csv
import os
import sys
from datetime import datetime

FORECAST_PROJECT_DIR = "/opt/crypto_forecast"
sys.path.insert(0, FORECAST_PROJECT_DIR)
os.chdir(FORECAST_PROJECT_DIR)

from dotenv import load_dotenv

load_dotenv()

HISTORY_FILE = os.getenv("HISTORY_FILE", "history.csv")


def read_history(coin_type=None):
    if not os.path.exists(HISTORY_FILE):
        return []
    
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if coin_type:
        rows = [r for r in rows if r.get("coin_type") == coin_type]
    
    return rows


def format_history(rows, limit=10):
    if not rows:
        return "📭 暂无历史预测记录"
    
    rows = rows[-limit:]
    
    coin_name = "BTC" if rows[0]["coin_type"] == "btc" else "ETH"
    
    result = f"📋 {coin_name} 历史预测记录（最近 {len(rows)} 条）\n"
    result += "-----------------------------------\n\n"
    
    for i, row in enumerate(reversed(rows), 1):
        dt = row["datetime"]
        price = float(row["price"])
        direction = row["direction"]
        confidence = float(row["confidence"]) * 100
        lower = float(row["predicted_lower"])
        upper = float(row["predicted_upper"])
        actual = row.get("actual_price", "")
        
        direction_emoji = {
            "bullish": "📈",
            "bullish_weak": "📈",
            "bearish": "📉",
            "bearish_weak": "📉",
            "neutral": "➡️",
        }.get(direction, "➡️")
        
        verified = ""
        if actual:
            actual_price = float(actual)
            if lower <= actual_price <= upper:
                verified = " ✓"
            else:
                verified = " ✗"
        
        result += f"#{i} {dt}\n"
        result += f"   价格: ${price:,.2f} | {direction_emoji} {direction} ({confidence:.1f}%)\n"
        result += f"   区间: ${lower:,.2f} ~ ${upper:,.2f}{verified}\n"
        result += "\n"
    
    result += "-----------------------------------\n"
    result += "✓ 表示实际价格在预测区间内，✗ 表示超出区间\n"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="查询历史预测记录")
    parser.add_argument("--coin", "-c", choices=["btc", "eth"], default="btc",
                        help="币种类型: btc 或 eth")
    parser.add_argument("--limit", "-n", type=int, default=10,
                        help="返回条数，默认 10 条")
    
    args = parser.parse_args()
    
    rows = read_history(args.coin)
    result = format_history(rows, args.limit)
    
    print(result)


if __name__ == "__main__":
    main()