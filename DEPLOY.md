# BTC/ETH 价格预测系统 - 部署指南

## 环境要求
- Linux 系统（Ubuntu/Debian/CentOS）
- Python 3.8+
- Git
- mihomo 代理（国内环境）

---

## 部署步骤

### 1. 克隆项目

```bash
sudo mkdir -p /opt/crypto_forecast
sudo chown $USER:$USER /opt/crypto_forecast
cd /opt/crypto_forecast
git clone https://github.com/你的用户名/crypto_forecast.git .
```

### 2. 创建虚拟环境并安装依赖

```bash
cd /opt/crypto_forecast
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

如果 pip 安装慢，使用国内源：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 3. 配置环境变量

```bash
cd /opt/crypto_forecast
cp .env .env.bak
vim .env
```

修改 `.env` 文件中的两个关键配置：

```env
# 飞书机器人 Webhook（必填）
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/你的Webhook地址

# 代理地址（国内环境必填）
PROXY_URL=http://127.0.0.1:7890
```

### 4. 设置脚本权限

```bash
chmod +x /opt/crypto_forecast/run_forecast.sh
```

### 5. 测试运行

```bash
cd /opt/crypto_forecast
source venv/bin/activate
python crypto_forecast.py
```

如果看到以下输出，说明部署成功：
```
✓ 价格数据获取成功
✓ 方向判断: 中性（82%概率随机游走）
✓ 波动区间预测: $xx,xxx ~ $xx,xxx
飞书消息发送成功
```

同时检查飞书群是否收到消息。

### 6. 配置 Hermes 定时任务

在 Hermes 管理界面添加定时任务：

| 配置项 | 值 |
|--------|-----|
| 任务名称 | crypto_forecast_hourly |
| 调度规则 | `0 * * * *`（每小时整点） |
| 运行模式 | no-agent |
| 执行命令 | `bash /opt/crypto_forecast/run_forecast.sh` |
| 超时时间 | 120秒 |
| 重试次数 | 2 |
| 重试间隔 | 60秒 |

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| API 连接失败 | 检查 mihomo 代理是否运行 |
| 飞书消息不推送 | 检查 `.env` 中的 Webhook 地址 |
| 定时任务不执行 | 检查 Hermes gateway 进程 |
| pip 安装失败 | 使用清华源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ...` |
| 权限不足 | `sudo chown -R $USER:$USER /opt/crypto_forecast` |

---

## 后续更新

代码更新后，在服务器执行：
```bash
cd /opt/crypto_forecast
git pull
```

---

## 目录结构

```
/opt/crypto_forecast/
├── .env                    # 配置文件
├── crypto_forecast.py      # 主脚本
├── data_fetchers.py        # 数据获取
├── indicators.py           # 技术指标
├── market_regime.py        # 市场状态识别
├── direction.py            # 方向评分
├── predict_range.py        # 波动区间预测
├── validation.py           # 验证机制
├── history.py              # 历史记录
├── feishu_notify.py        # 飞书推送
├── requirements.txt        # 依赖
├── run_forecast.sh         # 启动脚本
└── hermes_cron.json        # Hermes配置
```
