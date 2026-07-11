---
name: crypto-forecast
description: BTC/ETH 价格预测与查询技能 — 支持实时行情查询、历史记录查看、预测准确率统计
version: 1.0.0
author: hermes-trading
license: MIT
metadata:
  hermes:
    tags: [trading, crypto, btc, eth, forecast, price]
    related_skills: [web-search, research]
    requires_toolsets: [terminal]
    config:
      - key: crypto-forecast.webhook_url
        description: 飞书机器人 Webhook 地址
        default: ""
      - key: crypto-forecast.proxy_url
        description: 代理地址（国内环境）
        default: ""
---

# BTC/ETH 价格预测与查询技能

通过技术指标分析，为用户提供 BTC/ETH 的实时价格预测、历史记录查询和准确率统计。

## 何时使用

当用户请求以下任务时，加载此技能：
- "BTC 现在怎么样"
- "ETH 行情"
- "价格预测"
- "比特币"
- "以太坊"
- "帮我看看 BTC"
- "预测 BTC 价格"
- "查询历史预测"
- "预测准吗"
- "准确率"

包含以下关键词的请求：
- `BTC`、`ETH`、`比特币`、`以太坊`
- `价格`、`行情`、`预测`、`走势`
- `历史`、`记录`、`准确率`

## 架构说明

```
用户输入 → 意图识别 → 执行对应脚本 → 返回结果
                          ↓
              ┌───────────┴───────────┐
              ▼                       ▼
        实时预测              历史查询/统计
        forecast_now.py    history_query.py / stats.py
```

## 操作步骤

### 第 0 步：确认用户意图

从用户请求中提取以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `coin_type` | 币种类型 | btc（如果用户没指定） |
| `action` | 动作类型 | forecast（实时预测） |

**意图映射：**

| 用户输入示例 | action | coin_type |
|------------|--------|-----------|
| "BTC 现在怎么样" | forecast | btc |
| "ETH 行情" | forecast | eth |
| "预测 BTC 价格" | forecast | btc |
| "最近 10 次预测" | history | btc |
| "预测准吗" | stats | btc |
| "ETH 历史记录" | history | eth |

### 第 1 步：实时预测

执行脚本获取实时预测结果：

```bash
python3 ${HERMES_SKILL_DIR}/scripts/forecast_now.py --coin btc
```

返回格式：
```
💰 BTC 价格预测报告
-----------------------------------
📊 当前价格: $67,500.00
🎯 方向判断: 中性（82%概率随机游走）
   置信度: 74.0%
📏 波动区间: $67,230.00 ~ $67,770.00
   区间宽度: 0.80% (normal)
📈 市场状态: 低波动震荡 → 区间操作
✅ 上小时验证结果: ✓
-----------------------------------
💡 提示: BTC 在 1 小时周期上 82% 的时间是中性随机游走
```

### 第 2 步：查询历史记录

```bash
python3 ${HERMES_SKILL_DIR}/scripts/history_query.py --coin btc --limit 10
```

返回最近 N 条预测记录的摘要。

### 第 3 步：统计准确率

```bash
python3 ${HERMES_SKILL_DIR}/scripts/stats.py --coin btc
```

返回预测准确率统计，包括：
- 总预测次数
- 区间命中次数及准确率
- 方向命中次数及准确率
- 各方向预测的准确率分布

## 快速参考

| 命令 | 说明 |
|------|------|
| `BTC 现在怎么样` | 查询 BTC 实时预测 |
| `ETH 行情` | 查询 ETH 实时预测 |
| `最近 10 次预测` | 查询最近 10 条预测记录 |
| `预测准确率` | 统计预测准确率 |
| `市场状态` | 查看当前市场状态 |

## 技术要点

- **技术指标**：EMA(12/26)、RSI(14)、VWAP、布林带(20)、ATR(14)、K线动量
- **三层备援**：Coinlore → Binance → CoinGecko，任一 API 故障自动切换
- **自动验证**：每小时自动验证上一条预测准确性，写入历史记录

## 常见陷阱

- 如果网络不通（国内环境），需要配置代理地址
- 如果飞书 Webhook 未配置，无法推送定时消息
- 预测基于技术指标，不包含基本面分析，仅供参考

## 验证

报告生成后，检查以下要点：
- 当前价格是否获取成功
- 方向判断和置信度是否合理
- 波动区间是否符合市场状态
- 历史记录是否完整

---

**注意**：本技能仅提供技术分析参考，不构成投资建议。