# 项目进度 & 问题追踪

> 机器人和用户通过这个文件沟通，同步进展和待解决问题。

---

## 一、项目结构

```
competitive-analysis/
├── crypto_forecast.py          # BTC/ETH 价格预测主入口
├── data_fetchers.py            # 三层备援（Coinlore→Binance→CoinGecko）
├── indicators.py               # 技术指标（RSI、ATR、VWAP、布林带）
├── market_regime.py            # 市场状态识别
├── direction.py                # 方向评分
├── predict_range.py            # 波动区间预测
├── validation.py               # 验证机制（含空字符串float转换修复）
├── history.py                  # 历史CSV
├── feishu_notify.py            # 飞书推送
├── requirements.txt
├── hermes_cron.json            # Hermes定时任务配置
├── DEPLOY.md / INSTALL.md      # 部署指南
│
├── src/competitive_analysis/   # CrewAI 竞品分析系统
│   ├── crew.py                 # 3个Agent：市场调研、产品分析、战略顾问
│   ├── main.py
│   ├── config/agents.yaml
│   ├── config/tasks.yaml
│   └── tools/__init__.py
│
├── hermes-skill/research/competitive-analysis/  # Hermes Skill 格式
│   ├── SKILL.md
│   └── scripts/run_agent.py
│
├── crew-ai-analysis.md         # CrewAI 架构分析文档
├── hermes-info.md
├── run.sh / run_forecast.sh / deploy.sh
├── pyproject.toml
├── requirements.txt
├── .env                        # 环境变量
├── .gitignore
└── README.md
```

---

## 二、当前状态

### ✅ 已完成

| 事项 | 状态 | 说明 |
|------|------|------|
| GitHub 仓库同步 | ✅ | 本地与 origin/main 完全一致 |
| mihomo VPN 代理 | ✅ | 订阅更新后恢复，Binance/CoinGecko 可访问 |
| crypto_forecast.py 运行 | ✅ | BTC/ETH 预测正常，飞书消息发送成功 |
| validation.py Bug 修复 | ✅ | 空字符串 `''` 导致 `float()` 报错，已修复 |
| PROGRESS.md 上传 | ✅ | GitHub API 推送（git push 超时改用 API） |

### ⚠️ 待处理

| 事项 | 状态 | 说明 |
|------|------|------|
| CrewAI 未安装 | ⚠️ | `import crewai` 报错，需 `pip install crewai` |
| 飞书通知 | ⚠️ | 依赖 `APP_ID` / `APP_SECRET`，需确认配置 |

---

## 三、最近运行结果

```
BTC 价格: $63,871.47（来源: coinlore）
  市场状态: 正常波动下跌 → 趋势健康
  方向: 中性（82%概率随机游走），置信度 74.0%
  区间: $63,793 ~ $64,063（±0.4~0.8%）
  飞书: ✅ 发送成功

ETH 价格: $1,787.72（来源: coinlore）
  市场状态: 正常波动下跌 → 趋势健康
  方向: 温和看空（评分 -3，置信度 8.0%）
  区间: $1,778 ~ $1,795（±0.4~0.8%）
  飞书: ✅ 发送成功
  验证: 上小时区间✓ 方向✓
```

---

## 四、Git 操作记录

| 时间 | 操作 | 结果 |
|------|------|------|
| 2026-07-11 | 创建仓库 competitive-analysis | ✅ |
| 2026-07-11 | 删除 crypto_forecast 仓库 | ⚠️ 用户手动删除 |
| 2026-07-12 | 更新 mihomo 订阅配置 | ✅ 代理恢复 |
| 2026-07-12 | 修复 validation.py float 空字符串 bug | ✅ 已推送 |
| 2026-07-12 | 上传 PROGRESS.md | ✅ GitHub API |

---

## 五、下一步

- [ ] 安装 crewai：`pip install crewai`
- [ ] 确认飞书机器人配置
- [ ] 测试 CrewAI 竞品分析模块
