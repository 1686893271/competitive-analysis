#!/bin/bash
# 多 Agent 竞品分析报告生成器 - 启动脚本
#
# 使用方法:
#   ./run.sh
#   ./run.sh --company "OpenAI" --industry "大语言模型"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH" \
  "$SCRIPT_DIR/../crewai-env/bin/python" "$SCRIPT_DIR/src/competitive_analysis/main.py" "$@"
