#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_fetchers import (
    fetch_price_with_fallback,
    fetch_btc_1h_klines,
    fetch_eth_1h_klines,
)
from indicators import calc_rsi, calc_atr, calc_vwap
from market_regime import detect_market_regime, get_regime_description
from direction import score_direction, interpret, get_direction_confidence, get_direction_description
from predict_range import predict_range, get_range_width_description
from validation import check_and_verify_last, analyze_rules
from history import write_prediction, update_last_actual_price
from feishu_notify import send_feishu_message, format_feishu_report


def run_forecast(coin_type: str = "btc") -> dict:
    print(f"\n{'='*60}")
    print(f"  {coin_type.upper()} 价格预测 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    try:
        price_data = fetch_price_with_fallback(coin_type)
        price = price_data["price"]
        source = price_data["source"]
        percent_change_24h = price_data["percent_change_24h"]
        print(f"✓ 价格数据获取成功 (来源: {source})")
        print(f"  当前价格: ${price:,.2f}")
        print(f"  24h涨跌幅: {percent_change_24h:+.2f}%")
    except Exception as e:
        print(f"✗ 价格数据获取失败: {e}")
        return {"error": str(e)}

    if coin_type == "btc":
        klines = fetch_btc_1h_klines(limit=48)
    else:
        klines = fetch_eth_1h_klines(limit=48)

    if not klines:
        print("✗ K线数据获取失败")
        return {"error": "K线数据获取失败"}
    print(f"✓ K线数据获取成功 (最近 {len(klines)} 条)")

    verification = check_and_verify_last(price)
    if verification.get("verified"):
        print(f"✓ 上小时验证: {verification['message']}")

    regime = detect_market_regime(klines)
    regime_desc = get_regime_description(regime)
    print(f"✓ 市场状态识别: {regime_desc}")

    direction_score = score_direction(klines, price)
    direction = interpret(direction_score)
    confidence = get_direction_confidence(direction_score, direction)
    direction_desc = get_direction_description(direction)
    print(f"✓ 方向判断: {direction_desc} (评分: {direction_score}, 置信度: {confidence*100:.1f}%)")

    range_data = predict_range(price, klines)
    range_desc = get_range_width_description(range_data["width"])
    print(f"✓ 波动区间预测: ${range_data['lower']:,.2f} ~ ${range_data['upper']:,.2f} ({range_desc})")

    write_prediction(
        coin_type=coin_type,
        price=price,
        direction=direction,
        direction_score=direction_score,
        confidence=confidence,
        range_data=range_data,
        regime=regime,
        source=source,
        percent_change_24h=percent_change_24h,
    )

    report = format_feishu_report(
        coin_type=coin_type,
        price=price,
        direction=direction,
        direction_desc=direction_desc,
        confidence=confidence,
        range_data=range_data,
        regime=regime,
        regime_desc=regime_desc,
        verification=verification,
    )

    send_feishu_message(f"{coin_type.upper()} 价格预测报告", report)

    print(f"\n{'='*60}")
    print(f"  预测完成")
    print(f"{'='*60}")

    return {
        "success": True,
        "coin_type": coin_type,
        "price": price,
        "direction": direction,
        "direction_score": direction_score,
        "confidence": confidence,
        "range": range_data,
        "regime": regime,
        "verification": verification,
    }


def main():
    start_time = time.time()

    try:
        btc_result = run_forecast("btc")

        time.sleep(2)

        eth_result = run_forecast("eth")

        rules = analyze_rules(lookback_days=7)
        if "error" not in rules:
            print(f"\n{'='*60}")
            print(f"  近7天规律分析")
            print(f"{'='*60}")
            print(f"  总预测次数: {rules['total_predictions']}")
            print(f"  区间准确率: {rules['range_accuracy']}%")
            for direction, stats in rules["direction_stats"].items():
                print(f"  {direction}: {stats['total']}次, 准确率 {stats['accuracy']}%")
            print(f"{'='*60}")

        total_time = time.time() - start_time
        print(f"\n总耗时: {total_time:.2f}秒")

    except Exception as e:
        print(f"\n✗ 程序异常: {e}")
        import traceback
        traceback.print_exc()
        send_feishu_message("价格预测系统异常", f"程序运行异常: {str(e)}")


if __name__ == "__main__":
    main()