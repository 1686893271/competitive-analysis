# BTC/ETH 价格预测系统

> crypto_forecast.py v11 — 基于技术指标的短期价格预测系统，每小时运行，生成方向、波动区间、置信度报告并推送飞书。

---

## 目录

- [核心设计理念](#核心设计理念)
- [系统架构](#系统架构)
- [项目结构](#项目结构)
- [技术指标](#技术指标)
- [市场状态识别](#市场状态识别)
- [方向评分系统](#方向评分系统)
- [波动区间预测](#波动区间预测)
- [安装部署](#安装部署)
- [配置说明](#配置说明)
- [运行方式](#运行方式)
- [Hermes 定时任务配置](#hermes-定时任务配置)
- [飞书输出格式](#飞书输出格式)
- [CSV 历史记录格式](#csv-历史记录格式)
- [已知局限](#已知局限)

---

## 核心设计理念

| 原则 | 说明 |
|------|------|
| **宁可少做、不错做** | neutral 预测准确率 74%，bullish 仅 5%，bearish 仅 8% |
| **区间压缩到极致** | tight ±0.4%，normal ±0.4~0.8%，loose ±0.8%以上 |
| **多重确认** | RSI + VWAP + 布林带 + 动量 + EMA 交叉验证 |
| **三层备援** | Coinlore → Binance → CoinGecko，任一API故障自动切换 |
| **自动验证** | 每小时自动验证上一条预测准确性，写入历史 |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    数据获取层 (data_fetchers.py)                │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │  Coinlore    │ → │   Binance    │ → │  CoinGecko   │        │
│  │   (主源)     │   │   (备援1)    │   │   (备援2)    │        │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘        │
└─────────┼──────────────────┼──────────────────┼────────────────┘
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    技术指标层 (indicators.py)                   │
│  EMA(12/26) | RSI(14) | VWAP | 布林带(20) | ATR(14) | K线动量  │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ 市场状态识别      │ │ 方向评分系统      │ │ 波动区间预测      │
│ market_regime.py  │ │ direction.py      │ │ predict_range.py  │
└─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    输出层 (feishu_notify.py)                    │
│              格式化报告 → 飞书推送 → CSV历史记录                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 项目结构

| 文件 | 模块 | 功能 |
|------|------|------|
| `crypto_forecast.py` | 主脚本 | 串联所有模块，每小时运行 |
| `data_fetchers.py` | 数据获取 | 价格数据三层备援 + K线数据 |
| `indicators.py` | 技术指标 | EMA、RSI、VWAP、布林带、ATR、K线动量 |
| `market_regime.py` | 市场状态 | 高/低波动、上涨/下跌趋势识别 |
| `direction.py` | 方向判断 | score_direction + interpret 函数 |
| `predict_range.py` | 区间预测 | tight/normal/loose 波动区间 |
| `validation.py` | 验证机制 | check_and_verify_last + analyze_rules |
| `history.py` | 历史记录 | CSV持久化存储 |
| `feishu_notify.py` | 飞书推送 | 格式化报告推送 |
| `.env` | 配置文件 | 飞书Webhook、代理、日志路径 |
| `hermes_cron.json` | Hermes配置 | 定时任务JSON配置 |
| `run_forecast.sh` | 启动脚本 | Linux环境启动命令 |

---

## 技术指标

| 指标 | 参数 | 用途 |
|------|------|------|
| EMA | 12/26 | 趋势判断，均线交叉 |
| RSI | 14 | 超买超卖判断 (30/70) |
| VWAP | 当日累计 | 价格位置判断 |
| 布林带 | 20周期，2σ | 波动区间、突破信号 |
| ATR | 14 | 波动率度量 |
| ATR百分位 | 回溯100期 | 波动率相对水平 |
| K线动量 | 近4根 | 短期方向强度 |

---

## 市场状态识别

| 状态 | 描述 |
|------|------|
| `high_vol_bearish` | 高波动 + 超买 → 警惕回调 |
| `high_vol_bullish` | 高波动 + 超卖 → 可能反弹 |
| `high_vol` | 高波动状态 → 谨慎操作 |
| `low_vol_uptrend` | 低波动上涨 → 趋势稳定 |
| `low_vol_downtrend` | 低波动下跌 → 趋势稳定 |
| `low_vol_range` | 低波动震荡 → 区间操作 |
| `normal_uptrend` | 正常波动上涨 → 趋势健康 |
| `normal_downtrend` | 正常波动下跌 → 趋势健康 |
| `neutral` | 中性状态 → 观望为主 |

---

## 方向评分系统

`score_direction()` 返回评分（-10 ~ +10），`interpret()` 映射为方向：

| 评分范围 | 方向 | 描述 | 置信度 |
|---------|------|------|--------|
| ≥ 5 | `bullish` | 强烈看多 | 5% + (score-5)*1% |
| ≥ 3 | `bullish_weak` | 温和看多 | 5% |
| -2 ~ +2 | `neutral` | 中性 | 74% |
| ≤ -3 | `bearish_weak` | 温和看空 | 8% |
| ≤ -5 | `bearish` | 强烈看空 | 8% + (-score-5)*1% |

评分构成：
- RSI: ±1~2 分
- VWAP: ±1 分
- 布林带位置: ±1~2 分
- K线动量: ±1~2 分
- EMA交叉: ±1 分

---

## 波动区间预测

| 宽度类型 | ATR百分位条件 | 区间幅度 |
|---------|-------------|---------|
| `tight` | < 30% 或 ATR < 0.3% | ±0.4% |
| `normal` | 30%~70%，ATR 0.3%~1.2% | ±0.4%~0.8% |
| `loose` | > 70% 且 ATR > 1.2% | ±1.5% |

---

## 安装部署

### 环境要求

- Python 3.8+
- Linux/macOS/Windows（Linux 推荐用于 24h 运行）
- 网络访问：Coinlore、Binance、CoinGecko API
- 可选：mihomo 代理（用于国内环境）

### 安装步骤

```bash
# 克隆项目
git clone <repo-url>
cd crypto_forecast

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

## 配置说明

编辑 `.env` 文件：

```env
# 飞书机器人 Webhook 地址（必填）
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-token

# 代理地址（国内环境必填）
PROXY_URL=http://127.0.0.1:7890

# 币种ID（默认值即可）
BTC_ID=90
ETH_ID=80

# 日志配置
LOG_LEVEL=INFO
HISTORY_FILE=history.csv
LOG_FILE=crypto_forecast.log
```

---

## 运行方式

### 手动运行

```bash
source venv/bin/activate
python crypto_forecast.py
```

### 命令行参数

```bash
# 运行并输出详细日志
python crypto_forecast.py

# 后台运行（Linux）
nohup python crypto_forecast.py > forecast.log 2>&1 &
```

---

## Hermes 定时任务配置

### no-agent 模式（推荐）

`hermes_cron.json` 配置：

```json
{
    "name": "crypto_forecast_hourly",
    "description": "BTC/ETH 价格预测 - 每小时运行",
    "schedule": "0 * * * *",
    "mode": "no-agent",
    "command": "bash /opt/crypto_forecast/run_forecast.sh",
    "output": {
        "type": "feishu",
        "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-token"
    },
    "timeout": 120,
    "retry": 2,
    "retry_delay": 60
}
```

### 配置说明

| 字段 | 说明 |
|------|------|
| `schedule` | cron表达式，`0 * * * *` 表示每小时整点运行 |
| `mode` | `no-agent` 模式不消耗 Token，仅定时执行脚本 |
| `timeout` | 任务超时时间（秒） |
| `retry` | 失败重试次数 |
| `retry_delay` | 重试间隔（秒） |

### 小主机部署步骤

1. 将项目上传到 `/opt/crypto_forecast/`
2. 安装依赖并配置 `.env`
3. 在 Hermes 中导入 `hermes_cron.json`
4. 启动 Hermes 守护进程

---

## 飞书输出格式

```
💰 **BTC 价格预测报告**
-----------------------------------

📊 当前价格: **$67,500.00**

🎯 方向判断: **中性（82%概率随机游走）**
   置信度: **74.0%**

📏 波动区间: **$67,230.00 ~ $67,770.00**
   区间宽度: **0.80%** (normal)

📈 市场状态: **低波动震荡 → 区间操作**

✅ 上小时验证结果:
   预测区间验证: ✓ | 方向验证: ✓

-----------------------------------
💡 提示: BTC 在 1 小时周期上 82% 的时间是中性随机游走
         宁可少做、不错做 —— neutral 预测准确率 74%
```

---

## CSV 历史记录格式

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | float | Unix时间戳 |
| `datetime` | string | 格式化时间 |
| `coin_type` | string | btc/eth |
| `price` | float | 当前价格 |
| `direction` | string | bullish/bearish/neutral |
| `direction_score` | int | 方向评分 |
| `confidence` | float | 置信度 |
| `predicted_lower` | float | 预测下限 |
| `predicted_upper` | float | 预测上限 |
| `range_width` | string | tight/normal/loose |
| `range_pct` | float | 区间幅度(%) |
| `market_regime` | string | 市场状态 |
| `source` | string | 数据来源 |
| `percent_change_24h` | float | 24h涨跌幅 |
| `actual_price` | float | 实际价格（验证时填充） |

---

## 已知局限

1. **BTC 1小时周期 82% 为中性随机游走**：方向判断信号稀少且准确率低
2. **bullish/bearish 预测准确率仅 5%/8%**：强烈方向信号不可靠
3. **API 依赖外部服务**：需确保网络可达性，建议配置代理
4. **无 LLM 调用**：纯技术指标驱动，不包含基本面分析
5. **样本内拟合风险**：验证机制基于历史数据，未来市场可能变化

---

## License

MIT License