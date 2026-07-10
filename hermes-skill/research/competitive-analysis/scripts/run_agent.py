#!/usr/bin/env python3
"""
Hermes Skill — Multi-Agent 竞品分析报告生成器

辅助脚本：负责收集信息并整理为 Markdown 报告。
本脚本不依赖 CrewAI，直接通过文件 I/O 和结构化模板完成各阶段工作。

用法：
  python3 run_agent.py --agent market_researcher --company "CrewAI" --industry "多Agent框架" --output /tmp/ca_phase1.md
  python3 run_agent.py --agent product_analyst --company "CrewAI" --industry "多Agent框架" --input /tmp/ca_phase1.md --output /tmp/ca_phase2.md
  python3 run_agent.py --agent strategy_advisor --company "CrewAI" --industry "多Agent框架" --input /tmp/ca_phase1.md,/tmp/ca_phase2.md --output /tmp/report.md
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

AGENT_PROMPTS = {
    "market_researcher": """你是一位资深的行业分析师，拥有 10 年以上的市场研究经验。
你擅长分析行业趋势、竞争格局和技术发展方向。
请基于收集到的信息，撰写结构化的市场调研报告。

输出格式为 Markdown，包含以下部分：
## 行业概览
- 市场规模与增长趋势
- 关键驱动因素

## 主要竞争对手
对每个竞品，列出：
| 竞品名称 | 核心产品 | 市场定位 | 融资/规模 | 关键数据 |

## 行业发展趋势
- 技术方向
- 市场预测

## {company} 的竞争地位总结
""",

    "product_analyst": """你是一位经验丰富的产品分析师，对产品设计和用户体验有敏锐的洞察力。
请基于前期调研结果，对竞品进行深度产品功能对比分析。

输出格式为 Markdown，包含以下部分：
## 产品功能对比矩阵
| 功能维度 | {company} | 竞品1 | 竞品2 | 竞品3 |

## 技术架构对比

## 定价策略对比

## 用户体验评估

## {company} SWOT 分析
| 维度 | 分析 |
|------|------|
| 优势 (S) | |
| 劣势 (W) | |
| 机会 (O) | |
| 威胁 (T) | |
""",

    "strategy_advisor": """你是一位顶级的管理咨询顾问，曾在多家知名咨询公司任职。
你擅长将复杂的数据和分析结果整合为清晰、有说服力的战略报告。

请基于前两阶段的分析结果，撰写一份完整的竞品分析报告。

输出格式为 Markdown，包含以下部分：
# {company} 竞品分析报告

## 执行摘要
（一页纸总结核心发现和建议）

## 一、行业概况与市场格局

## 二、竞品详细对比分析

## 三、{company} SWOT 分析

## 四、战略建议
### 短期（1-3 个月）
### 中期（3-6 个月）
### 长期（6-12 个月）

## 五、附录
### 数据来源
### 分析方法说明

---
*报告生成时间：{timestamp}*
*本报告由 Multi-Agent 协作系统自动生成*
""",
}


def read_input_files(input_paths: str) -> str:
    """读取逗号分隔的输入文件"""
    contents = []
    for path in input_paths.split(","):
        p = Path(path.strip())
        if p.exists():
            contents.append(f"--- 来源: {p.name} ---\n{p.read_text(encoding='utf-8')}\n")
        else:
            contents.append(f"--- 来源: {p.name} (文件不存在) ---\n")
    return "\n".join(contents)


def generate_template(agent: str, company: str, industry: str, input_content: str = "") -> str:
    """生成带上下文的报告模板"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prompt = AGENT_PROMPTS.get(agent, "")
    prompt = prompt.replace("{company}", company)
    prompt = prompt.replace("{timestamp}", timestamp)

    parts = [
        f"# Agent: {agent}",
        f"# 分析对象: {company}",
        f"# 所属行业: {industry}",
        f"# 生成时间: {timestamp}",
        "",
        "=" * 60,
        "",
    ]

    if input_content:
        parts.append("## 前序阶段的输入\n")
        parts.append(input_content)
        parts.append("")
        parts.append("=" * 60)
        parts.append("")

    parts.append("## 你的任务\n")
    parts.append(prompt)
    parts.append("")
    parts.append("请根据上述信息，填充报告内容。如果信息不足，请标注 [待补充] 并给出你的合理推断。")
    parts.append("")
    parts.append("---")
    parts.append("注意：本模板由 Hermes Skill 辅助脚本生成。Hermes Agent 应基于此模板和搜索到的信息完成报告。")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Hermes Skill — 竞品分析 Agent 辅助脚本")
    parser.add_argument("--agent", required=True, choices=["market_researcher", "product_analyst", "strategy_advisor"],
                        help="Agent 角色")
    parser.add_argument("--company", required=True, help="要分析的公司/产品")
    parser.add_argument("--industry", required=True, help="所属行业")
    parser.add_argument("--input", default="", help="前序阶段输出文件路径（逗号分隔）")
    parser.add_argument("--output", required=True, help="输出文件路径")

    args = parser.parse_args()

    input_content = read_input_files(args.input) if args.input else ""
    template = generate_template(args.agent, args.company, args.industry, input_content)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template, encoding="utf-8")

    print(f"[OK] {args.agent} 模板已生成: {args.output}")
    print(f"     Hermes Agent 应基于此模板和搜索到的信息完成报告填充。")


if __name__ == "__main__":
    main()
