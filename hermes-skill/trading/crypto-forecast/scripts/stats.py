#!/usr/bin/env python3
# coding: utf-8

import argparse
import csv
import os
import sys
from datetime import datetime, timedelta

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


def calculate_stats(rows):
    if not rows:
        return {"error": "暂无历史记录"}
    
    total = len(rows)
    
    rows_with_actual = [r for r in rows if r.get("actual_price") and float(r["actual_price"]) > 0]
    verified_total = len(rows_with_actual)
    
    range_correct = 0
    direction_correct = 0
    
    direction_stats = {}
    
    for row in rows_with_actual:
        try:
            actual_price = float(row["actual_price"])
            predicted_lower = float(row["predicted_lower"])
            predicted_upper = float(row["predicted_upper"])
            predicted_price = float(row["price"])
            direction = row.get("direction", "unknown")
        except (KeyError, ValueError):
            continue
        
        in_range = predicted_lower <= actual_price <= predicted_upper
        if in_range:
            range_correct += 1
        
        if direction == "neutral":
            dir_correct = in_range
        elif direction in ("bullish", "bullish_weak"):
            dir_correct = actual_price >= predicted_price
        elif direction in ("bearish", "bearish_weak"):
            dir_correct = actual_price <= predicted_price
        else:
            dir_correct = False
        
        if dir_correct:
            direction_correct += 1
        
        if direction not in direction_stats:
            direction_stats[direction] = {"total": 0, "correct": 0}
        direction_stats[direction]["total"] += 1
        if dir_correct:
            direction_stats[direction]["correct"] += 1
    
    range_accuracy = (range_correct / verified_total) * 100 if verified_total > 0 else 0
    direction_accuracy = (direction_correct / verified_total) * 100 if verified_total > 0 else 0
    
    for d in direction_stats:
        total_d = direction_stats[d]["total"]
        direction_stats[d]["accuracy"] = (direction_stats[d]["correct"] / total_d) * 100 if total_d > 0 else 0
    
    return {
        "total_predictions": total,
        "verified_predictions": verified_total,
        "range_accuracy": round(range_accuracy, 1),
        "direction_accuracy": round(direction_accuracy, 1),
        "direction_stats": direction_stats,
    }


def format_stats(stats, coin_type):
    if stats.get("error"):
        return f"❌ {stats['error']}"
    
    coin_name = "BTC" if coin_type == "btc" else "ETH"
    
    result = f"📊 {coin_name} 预测准确率统计\n"
    result += "-----------------------------------\n\n"
    result += f"📈 总预测次数: {stats['total_predictions']}\n"
    result += f"✅ 已验证次数: {stats['verified_predictions']}\n\n"
    
    result += f"🎯 区间预测准确率: **{stats['range_accuracy']}%**\n"
    result += f"🎯 方向预测准确率: **{stats['direction_accuracy']}%**\n\n"
    
    result += "📋 各方向准确率:\n"
    for direction, d_stats in sorted(stats["direction_stats"].items()):
        emoji = {
            "bullish": "📈",
            "bullish_weak": "📈",
            "bearish": "📉",
            "bearish_weak": "📉",
            "neutral": "➡️",
        }.get(direction, "➡️")
        result += f"   {emoji} {direction}: {d_stats['total']}次, 准确率 {d_stats['accuracy']:.1f}%\n"
    
    result += "\n-----------------------------------\n"
    result += "💡 提示: 区间预测准确率更具参考价值\n"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="统计预测准确率")
    parser.add_argument("--coin", "-c", choices=["btc", "eth"], default="btc",
                        help="币种类型: btc 或 eth")
    
    args = parser.parse_args()
    
    rows = read_history(args.coin)
    stats = calculate_stats(rows)
    result = format_stats(stats, args.coin)
    
    print(result)


if __name__ == "__main__":
    main()