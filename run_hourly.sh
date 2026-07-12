#!/bin/bash
# 安装 BTC/ETH 价格预测系统定时任务
# 用法: bash run_hourly.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/../crypto_report/venv/bin/python3"
PYTHON="${VENV_PYTHON:-$SCRIPT_DIR/venv/bin/python3}"
CRON_LINE="0 * * * * cd $SCRIPT_DIR && $PYTHON crypto_forecast.py >> $SCRIPT_DIR/cron.log 2>&1"

echo "=== BTC/ETH 定时任务安装 ==="
echo "脚本路径: $SCRIPT_DIR"
echo "Python: $PYTHON"
echo ""

# 检查 Python 路径
if [ ! -f "$PYTHON" ]; then
    echo "[错误] 找不到 Python: $PYTHON"
    echo "请先创建虚拟环境: python3 -m venv venv"
    exit 1
fi

# 检查 crypto_forecast.py
if [ ! -f "$SCRIPT_DIR/crypto_forecast.py" ]; then
    echo "[错误] 找不到 crypto_forecast.py"
    exit 1
fi

# 检查是否已有该定时任务
EXISTING=$(crontab -l 2>/dev/null | grep -F "$SCRIPT_DIR/crypto_forecast.py")
if [ -n "$EXISTING" ]; then
    echo "[提示] 定时任务已存在:"
    echo "$EXISTING"
    echo ""
    echo "删除旧任务请运行: crontab -l | grep -v crypto_forecast.py | crontab -"
    exit 0
fi

# 追加定时任务
(crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
echo "[成功] 定时任务已安装!"
echo "任务内容: $CRON_LINE"
echo ""
echo "查看定时任务: crontab -l"
echo "查看运行日志: tail -f $SCRIPT_DIR/cron.log"
