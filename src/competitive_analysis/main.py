#!/usr/bin/env python3
"""
多 Agent 竞品分析报告生成器

基于 CrewAI 框架，通过 3 个专业化 Agent 协作完成：
  1. 市场调研专家 → 收集行业数据和竞争格局
  2. 产品分析师 → 深度产品功能对比
  3. 战略顾问 → 整合报告与战略建议

使用方法：
  python main.py
  # 或指定自定义参数
  python main.py --company "OpenAI" --industry "大语言模型"
"""

import sys
import argparse
from competitive_analysis.crew import CompetitiveAnalysisCrew


def run(company: str = "CrewAI", industry: str = "多 Agent AI 框架") -> None:
    """运行竞品分析 Crew"""
    inputs = {
        'company': company,
        'industry': industry,
    }

    print(f"\n{'='*60}")
    print(f"  多 Agent 竞品分析报告生成器")
    print(f"  分析对象: {company}")
    print(f"  所属行业: {industry}")
    print(f"{'='*60}\n")

    try:
        result = CompetitiveAnalysisCrew().crew().kickoff(inputs=inputs)
        print(f"\n{'='*60}")
        print("  报告生成完成！")
        print(f"  输出文件: competitive_analysis_report.md")
        print(f"{'='*60}\n")
        return result
    except Exception as e:
        print(f"\n执行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="多 Agent 竞品分析报告生成器")
    parser.add_argument(
        "--company", type=str, default="CrewAI",
        help="要分析的公司/产品名称 (默认: CrewAI)"
    )
    parser.add_argument(
        "--industry", type=str, default="多 Agent AI 框架",
        help="所属行业 (默认: 多 Agent AI 框架)"
    )
    args = parser.parse_args()

    run(company=args.company, industry=args.industry)
