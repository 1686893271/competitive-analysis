#!/bin/bash

set -e

HOST="your-host-ip"
USER="your-username"
REMOTE_DIR="/opt/crypto_forecast"
LOCAL_DIR=$(dirname "$0")

echo "========================================"
echo "  BTC/ETH 价格预测系统 - 部署脚本"
echo "========================================"

echo ""
echo "步骤1: 创建远程目录..."
ssh "$USER@$HOST" "mkdir -p $REMOTE_DIR"

echo ""
echo "步骤2: 上传文件..."
scp -r "$LOCAL_DIR/"* "$USER@$HOST:$REMOTE_DIR/"

echo ""
echo "步骤3: 安装依赖..."
ssh "$USER@$HOST" "cd $REMOTE_DIR && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

echo ""
echo "步骤4: 配置环境变量..."
ssh "$USER@$HOST" "cd $REMOTE_DIR && cp .env .env.example || true"

echo ""
echo "========================================"
echo "  部署完成!"
echo ""
echo "请在小主机上执行以下操作:"
echo "  1. 编辑 $REMOTE_DIR/.env"
echo "     - 设置 FEISHU_WEBHOOK_URL"
echo "     - 设置 PROXY_URL (国内环境)"
echo ""
echo "  2. 测试运行:"
echo "     cd $REMOTE_DIR && source venv/bin/activate && python crypto_forecast.py"
echo ""
echo "  3. 配置 Hermes 定时任务:"
echo "     - 导入 hermes_cron.json"
echo "     - schedule: \"0 * * * *\""
echo "     - mode: \"no-agent\""
echo "========================================"