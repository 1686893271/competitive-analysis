# 项目进度 & 问题追踪

> 机器人和用户通过这个文件沟通，同步进展和待解决问题。

---

## 一、项目结构

```
competitive-analysis/
├── crypto_forecast/          # BTC/ETH 价格预测系统（主系统）
│   ├── crypto_forecast.py   # 主入口
│   ├── data_fetchers.py     # 数据获取（三层备援：Coinlore→Binance→CoinGecko）
│   ├── indicators.py        # 技术指标（RSI、ATR、VWAP、布林带）
│   ├── market_regime.py     # 市场状态识别
│   ├── direction.py         # 方向评分
│   ├── predict_range.py     # 波动区间预测
│   ├── validation.py        # 验证机制
│   ├── history.py           # 历史CSV
│   ├── feishu_notify.py     # 飞书推送
│   ├── requirements.txt     # 依赖
│   ├── hermes_cron.json     # Hermes定时任务配置
│   └── DEPLOY.md            # 部署指南
│
├── src/competitive_analysis/ # CrewAI 竞品分析系统
│   ├── crew.py              # 3个Agent：市场调研、产品分析、战略顾问
│   ├── main.py              # 主入口
│   ├── config/agents.yaml   # Agent配置
│   ├── config/tasks.yaml    # Task配置
│   └── tools/__init__.py
│
├── hermes-skill/research/competitive-analysis/  # Hermes Skill 格式
│   ├── SKILL.md
│   └── scripts/run_agent.py
│
├── crew-ai-analysis.md      # CrewAI 架构分析文档
├── hermes-info.md           # Hermes 信息
├── INSTALL.md               # 安装指南
├── run.sh / run_forecast.sh # 运行脚本
├── deploy.sh                # 部署脚本
├── pyproject.toml
├── requirements.txt
├── .env                     # 环境变量（已gitignore）
├── .gitignore
└── README.md
```

---

## 二、当前状态

### 2.1 已完成
- [x] GitHub 仓库已创建（1686893271/competitive-analysis）
- [x] 本地与 GitHub 完全同步
- [x] `crypto_forecast.py` 可独立运行（Python 依赖已满足）
- [x] CrewAI 竞品分析模块存在（`src/competitive_analysis/`）

### 2.2 待解决问题

#### 问题1：mihomo VPN 隧道不通
- **现象**：mihomo 进程运行正常（7890端口），但上游服务器 `nni.gfw2500.com:22443` 连接超时
- **影响**：Binance / CoinGecko / Google 所有境外 API 均无法访问
- **日志**：`[TCP] dial 代理 (match Match/) --> api.binance.com:443 error: nni.gfw2500.com:22443 connect error: i/o timeout`
- **原因**：VPN 订阅可能过期
- **解决**：到 wjkc66.vip 续费订阅，更新 mihomo 配置后重启

#### 问题2：CrewAI 未安装
- **现象**：`import crewai` 报 `ModuleNotFoundError`
- **解决**：`pip install crewai`

#### 问题3：飞书通知未配置
- **现象**：`feishu_notify.py` 需要正确的 `APP_ID` / `APP_SECRET`
- **解决**：填写 `.env` 中的飞书配置

---

## 三、Git 操作记录

| 时间 | 操作 | 结果 |
|------|------|------|
| 2026-07-11 | 初始化 git 仓库（crypto_forecast → competitive-analysis） | ✅ 完成 |
| 2026-07-11 | 删除多余仓库（crypto_forecast） | ⚠️ Token无删除权限，用户手动删除 |
| 2026-07-11 | 同步 trae/agent-71Quk4 分支到 main | ✅ 完成 |
| 2026-07-11 | 整理项目结构，上传 PROGRESS.md | ⏳ 待上传 |

---

## 四、下一步行动

### 机器人负责：
1. [ ] 续 VPN 后重启 mihomo，验证代理可用
2. [ ] 安装 crewai 依赖
3. [ ] 测试 crypto_forecast.py 完整运行
4. [ ] 上传 PROGRESS.md 到 GitHub

### 用户负责：
1. [ ] 续费 VPN 订阅（wjkc66.vip）
2. [ ] 确认飞书机器人配置
