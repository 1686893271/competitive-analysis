# 多 Agent 竞品分析报告生成器

基于 [CrewAI](https://github.com/joaomdmoura/crewAI) 框架的多 Agent 协作系统实践项目。

## 架构

```
用户输入 (公司名 + 行业)
        │
        ▼
┌──────────────┐    调研报告     ┌──────────────┐    分析报告     ┌──────────────┐
│ 市场调研专家  │ ────────────── │ 产品分析师    │ ────────────── │ 战略顾问      │
│              │                │              │                │              │
│ · 行业规模   │                │ · 功能对比   │                │ · SWOT 分析  │
│ · 竞争格局   │                │ · 技术架构   │                │ · 战略建议   │
│ · 市场份额   │                │ · 定价策略   │                │ · 完整报告   │
│ · 发展趋势   │                │ · 用户体验   │                │ · 执行摘要   │
└──────────────┘                └──────────────┘                └──────────────┘
```

## 快速开始

```bash
# 1. 安装依赖
pip install crewai crewai-tools

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env 填入你的 OpenAI API Key

# 3. 运行
python src/competitive_analysis/main.py
# 或自定义分析对象
python src/competitive_analysis/main.py --company "OpenAI" --industry "大语言模型"
```

## 核心概念

- **Agent（智能体）**: 扮演特定角色的 AI 助手，拥有独立的系统提示词和目标
- **Task（任务）**: Agent 需要完成的具体工作单元
- **Crew（团队）**: 多个 Agent 和 Task 的编排单元，定义执行流程
- **Process（流程）**: 任务执行模式，本项目使用 Sequential（顺序执行）
