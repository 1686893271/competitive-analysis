# BTC/ETH 价格预测系统 - 安装指南

> 版本：v11 | 部署目标：小主机（Linux）+ Hermes 框架

---

## 📋 前置条件

- [x] 小主机已安装 Linux（Ubuntu/Debian/CentOS 均可）
- [x] 小主机已安装 Python 3.8+
- [x] 小主机已配置 mihomo 代理（国内环境）
- [x] 已获取飞书机器人 Webhook 地址
- [x] 已安装 Hermes 框架

---

## 🔧 安装步骤

### 步骤1：克隆项目（Git方式）

```bash
# 创建项目目录
sudo mkdir -p /opt/crypto_forecast
sudo chown $USER:$USER /opt/crypto_forecast

# 进入目录并克隆仓库
cd /opt/crypto_forecast
git clone https://github.com/你的用户名/crypto_forecast.git .
```

> **注意**: 将 `https://github.com/你的用户名/crypto_forecast.git` 替换为你的实际仓库地址

**后续更新**：
```bash
cd /opt/crypto_forecast
git pull
```

---

#### 备用上传方式（如果不能用Git）

| 方式 | 命令 |
|------|------|
| **scp** | `scp -r crypto_forecast/* user@小主机IP:/opt/crypto_forecast/` |
| **SFTP** | 使用 FileZilla/WinSCP 拖放文件 |
| **打包** | `zip -r crypto_forecast.zip crypto_forecast/` → `scp` → `unzip` |

---

#### ✅ 验证上传结果

```bash
# 检查文件
ls -la /opt/crypto_forecast/
```

**预期输出**：
```
total 128
drwxr-xr-x  3 user user 4096 Jul  8 10:00 .
drwxr-xr-x  2 user user 4096 Jul  8 10:00 venv
-rw-r--r--  1 user user  137 Jul  8 10:00 .env
-rw-r--r--  1 user user 4096 Jul  8 10:00 crypto_forecast.py
-rw-r--r--  1 user user 2048 Jul  8 10:00 data_fetchers.py
-rw-r--r--  1 user user 1024 Jul  8 10:00 direction.py
-rw-r--r--  1 user user 1536 Jul  8 10:00 feishu_notify.py
-rw-r--r--  1 user user 1024 Jul  8 10:00 history.py
-rw-r--r--  1 user user 2048 Jul  8 10:00 indicators.py
-rw-r--r--  1 user user 1024 Jul  8 10:00 market_regime.py
-rw-r--r--  1 user user 1024 Jul  8 10:00 predict_range.py
-rw-r--r--  1 user user   62 Jul  8 10:00 requirements.txt
-rw-r--r--  1 user user   58 Jul  8 10:00 run_forecast.sh
-rw-r--r--  1 user user 1536 Jul  8 10:00 validation.py
```

### 步骤2：安装依赖

```bash
cd /opt/crypto_forecast
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 步骤3：配置环境变量

```bash
vim .env
```

修改以下配置：

```env
# ========== 必填配置 ==========
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/替换为你的Webhook地址

# ========== 国内环境必填 ==========
PROXY_URL=http://127.0.0.1:7890

# ========== 以下默认即可 ==========
BTC_ID=90
ETH_ID=80
LOG_LEVEL=INFO
HISTORY_FILE=history.csv
LOG_FILE=crypto_forecast.log
```

### 步骤4：测试运行

```bash
cd /opt/crypto_forecast
source venv/bin/activate
python crypto_forecast.py
```

**预期输出：**

```
============================================================
  BTC 价格预测 - 2026-07-08 10:00:00
============================================================
✓ 价格数据获取成功 (来源: coinlore)
  当前价格: $67,500.00
  24h涨跌幅: +2.35%
✓ K线数据获取成功 (最近 48 条)
✓ 市场状态识别: 低波动震荡 → 区间操作
✓ 方向判断: 中性（82%概率随机游走） (评分: 0, 置信度: 74.0%)
✓ 波动区间预测: $67,230.00 ~ $67,770.00 (正常区间（±0.4~0.8%）)
预测记录已写入: 2026-07-08 10:00:00
飞书消息发送成功
============================================================
  预测完成
============================================================
```

---

## ⏰ Hermes 定时任务配置

### 添加定时任务

在 Hermes 管理界面添加以下配置：

| 配置项 | 值 |
|--------|-----|
| **任务名称** | crypto_forecast_hourly |
| **任务描述** | BTC/ETH 价格预测 - 每小时运行 |
| **调度规则** | `0 * * * *` |
| **运行模式** | no-agent |
| **执行命令** | `bash /opt/crypto_forecast/run_forecast.sh` |
| **超时时间** | 120秒 |
| **重试次数** | 2 |
| **重试间隔** | 60秒 |

### run_forecast.sh 内容

确认 `/opt/crypto_forecast/run_forecast.sh` 内容如下：

```bash
#!/bin/bash
cd /opt/crypto_forecast
source venv/bin/activate
python crypto_forecast.py
```

确保脚本有执行权限：

```bash
chmod +x /opt/crypto_forecast/run_forecast.sh
```

---

## ✅ 验证部署

### 1. 检查飞书消息

运行后，飞书群应收到类似以下消息：

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

### 2. 检查历史记录

```bash
cat /opt/crypto_forecast/history.csv
```

### 3. 检查定时任务

等待一小时后，检查 `history.csv` 是否新增记录。

---

## ❌ 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| API 连接失败 | 网络不通 | 检查 mihomo 代理是否运行 |
| 飞书消息不推送 | Webhook 错误 | 重新获取飞书机器人 Webhook |
| 定时任务不执行 | Hermes 进程异常 | 重启 Hermes gateway |
| Python 版本错误 | 系统默认 Python2 | 使用 `python3` 命令 |
| 权限不足 | 目录权限问题 | `sudo chown -R $USER:$USER /opt/crypto_forecast` |
| 依赖安装失败 | pip 源问题 | `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt` |

---

## 📞 联系方式

如有问题，请联系：[你的联系方式]

---

## 📝 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-07-08 | v11 | 初始版本 |