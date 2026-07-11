#!/usr/bin/env python3
# coding: utf-8

import argparse
import os
import sys

FORECAST_PROJECT_DIR = "/opt/crypto_forecast"
sys.path.insert(0, FORECAST_PROJECT_DIR)

os.chdir(FORECAST_PROJECT_DIR)

from data_fetchers import (
    fetch_price_with_fallback,
    fetch_btc_1h_klines,
    fetch_eth_1h_klines,
)
from market_regime import detect_market_regime, get_regime_description
from direction import score_direction, interpret, get_direction_confidence, get_direction_description
from predict_range import predict_range, get_range_width_description
from validation import check_and_verify_last


def format_report(coin_type, price, direction, direction_desc, confidence,
                  range_data, regime, regime_desc, verification):
    coin_name = "BTC" if coin_type == "btc" else "ETH"
    
    report = f"💰 **{coin_name} 价格预测报告**\n"
    report += f"-----------------------------------\n\n"
    report += f"📊 当前价格: **${price:,.2f}**\n\n"
    report += f"🎯 方向判断: **{direction_desc}**\n"
    report += f"   置信度: **{confidence * 100:.1f}%**\n\n"
    report += f"📏 波动区间: **${range_data['lower']:,.2f} ~ ${range_data['upper']:,.2f}**\n"
    report += f"   区间宽度: **{range_data['range_pct']:.2f}%** ({range_data['width']})\n\n"
    report += f"📈 市场状态: **{regime_desc}**\n\n"
    
    if verification and verification.get("verified"):
        report += f"✅ 上小时验证结果: {verification['message']}\n\n"
    
    report += f"-----------------------------------\n"
    report += f"💡 提示: BTC 在 1 小时周期上 82% 的时间是中性随机游走\n"
    report += f"         宁可少做、不错做 —— neutral 预测准确率 74%\n"
    
    return report


def run_forecast_now(coin_type):
    try:
        price_data = fetch_price_with_fallback(coin_type)
        price = price_data["price"]
        
        if coin_type == "btc":
            klines = fetch_btc_1h_klines(limit=48)
        else:
            klines = fetch_eth_1h_klines(limit=48)
        
        if not klines:
            return {"error": "K线数据获取失败"}
        
        verification = check_and_verify_last(price)
        
        regime = detect_market_regime(klines)
        regime_desc = get_regime_description(regime)
        
        direction_score = score_direction(klines, price)
        direction = interpret(direction_score)
        confidence = get_direction_confidence(direction_score, direction)
        direction_desc = get_direction_description(direction)
        
        range_data = predict_range(price, klines)
        
        report = format_report(
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
        
        return {"success": True, "report": report}
    
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="BTC/ETH 实时价格预测")
    parser.add_argument("--coin", "-c", choices=["btc", "eth"], default="btc",
                        help="币种类型: btc 或 eth")
    
    args = parser.parse_args()
    
    result = run_forecast_now(args.coin)
    
    if result.get("success"):
        print(result["report"])
    else:
        print(f"❌ 预测失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()