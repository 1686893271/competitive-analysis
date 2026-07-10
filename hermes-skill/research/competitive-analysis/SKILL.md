---
name: competitive-analysis
description: Multi-Agent 竞品分析报告生成器 — 通过多角色协作完成市场调研、产品分析和战略建议
version: 1.0.0
author: 1686893271
license: MIT
metadata:
  hermes:
    tags: [research, multi-agent, analysis, report]
    related_skills: [web-search, research]
    requires_toolsets: [terminal]
    config:
      - key: competitive-analysis.default_model
        description: 用于分析的 LLM 模型
        default: ""
        prompt: "留空则使用 Hermes 默认模型"
---

# Multi-Agent 竞品分析报告生成器

通过 3 个专业化 Agent 角色协作，对指定公司/产品在目标行业中生成完整的竞品分析报告。

## 何时使用

当用户请求以下任务时，加载此技能：
- "帮我分析 XX 的竞品"
- "生成 XX 行业的竞争格局报告"
- "分析 XX 和 YY 的产品对比"
- "做一份 XX 的竞品分析"
- "competitive analysis for XX"
- 包含"竞品"、"竞争格局"、"市场分析"、"竞对分析"等关键词的请求

## 架构说明

本技能模拟多 Agent 协作系统，采用 **顺序编排** 模式：

```
用户输入 → [Agent 1: 市场调研专家] → [Agent 2: 产品分析师] → [Agent 3: 战略顾问] → 报告输出
```

每个 Agent 是一个独立的执行阶段，前一阶段的输出作为下一阶段的输入。

### Agent 角色定义

**Agent 1 — 市场调研专家**
- 目标：深入调研目标公司在目标行业中的竞争格局
- 输出：行业概览、主要竞品列表、市场份额数据、发展趋势

**Agent 2 — 产品分析师**
- 目标：基于调研结果，对竞品进行深度产品功能对比
- 输入：Agent 1 的调研报告
- 输出：功能对比矩阵、技术架构分析、定价策略对比、SWOT 分析

**Agent 3 — 战略顾问**
- 目标：整合前两阶段结果，撰写完整竞品分析报告
- 输入：Agent 1 + Agent 2 的报告
- 输出：包含执行摘要、详细分析、战略建议的完整 Markdown 报告

## 操作步骤

### 第 0 步：确认分析参数

从用户请求中提取或确认以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `company` | 要分析的公司/产品名称 | 需用户指定 |
| `industry` | 所属行业 | 需用户指定 |

如果用户未明确提供，先通过对话确认后再继续。

### 第 1 步：执行 Agent 1 — 市场调研

使用 `web_extract` 或 `web_search` 工具收集信息，然后用模型整理为结构化报告。

**调研内容**：
1. 分析 `{industry}` 行业的整体市场规模、增长趋势和关键驱动因素
2. 识别 `{company}` 的主要竞争对手（至少 3-5 家）
3. 收集每个竞争对手的核心数据：市场份额、融资情况、用户规模、核心产品
4. 分析行业技术发展趋势和未来方向
5. 总结 `{company}` 当前在行业中的竞争地位

**执行方式**：
```bash
python3 ${HERMES_SKILL_DIR}/scripts/run_agent.py \
  --agent market_researcher \
  --company "COMPANY" \
  --industry "INDUSTRY" \
  --output /tmp/ca_phase1.md
```

脚本会调用 `web_extract` 搜索相关信息，然后用 LLM 整理成结构化报告。

如果脚本执行失败，回退到手动模式：
- 用 `web_search` 搜索 "COMPANY INDUSTRY competitors market share"
- 用 `web_extract` 抓取关键页面
- 用模型整理成报告，保存到 `/tmp/ca_phase1.md`

### 第 2 步：执行 Agent 2 — 产品分析

基于 `/tmp/ca_phase1.md` 的调研结果，进行深度产品功能对比。

**分析内容**：
1. 逐一分析各竞品的核心产品功能列表
2. 对比各产品的技术架构和实现方案
3. 分析各产品的目标用户群体和定价策略
4. 评估各产品的用户体验和口碑
5. 识别 `{company}` 的核心竞争优势和需要改进的方向

**执行方式**：
```bash
python3 ${HERMES_SKILL_DIR}/scripts/run_agent.py \
  --agent product_analyst \
  --company "COMPANY" \
  --industry "INDUSTRY" \
  --input /tmp/ca_phase1.md \
  --output /tmp/ca_phase2.md
```

### 第 3 步：执行 Agent 3 — 战略报告

综合前两阶段结果，撰写完整报告。

**报告结构**：
1. 执行摘要（一页纸总结核心发现）
2. 行业概况与市场格局
3. 竞品详细对比分析（含对比表格）
4. `{company}` SWOT 分析
5. 战略建议（短期、中期、长期）
6. 附录：数据来源与分析方法说明

**执行方式**：
```bash
python3 ${HERMES_SKILL_DIR}/scripts/run_agent.py \
  --agent strategy_advisor \
  --company "COMPANY" \
  --industry "INDUSTRY" \
  --input /tmp/ca_phase1.md,/tmp/ca_phase2.md \
  --output /tmp/competitive_analysis_report.md
```

### 第 4 步：交付报告

将最终报告内容直接发送给用户。如果报告较长（超过 4000 字符），保存为文件并告知用户路径。

## 快速参考

| 命令 | 说明 |
|------|------|
| `/competitive-analysis CrewAI 多Agent框架` | 分析 CrewAI 在多 Agent 框架行业的竞品 |
| `/competitive-analysis OpenAI 大语言模型` | 分析 OpenAI 在 LLM 行业的竞品 |

## 技术要点（简历素材）

本项目演示了以下多 Agent 协作系统核心技术：

- **角色分工 (Role-based Collaboration)**：3 个专业化 Agent 角色，各有独立的系统提示词和目标
- **顺序编排 (Sequential Orchestration)**：任务链式传递，Agent 1 → Agent 2 → Agent 3
- **上下文传递 (Context Passing)**：前一阶段的输出作为下一阶段的输入
- **工具调用 (Tool Use)**：Agent 通过 web 搜索和 LLM 推理完成实际工作

## 常见陷阱

- 如果 `{company}` 是非常小众的产品，搜索结果可能不足，建议用户补充已知竞品
- 如果 Hermes 的 web 工具未配置 API Key（如 FIRECRAWL_API_KEY），搜索功能可能受限
- 脚本依赖 Python 3.10+，确保 Hermes 环境中 Python 版本兼容

## 验证

报告生成后，检查以下要点：
- 是否包含至少 3 个竞品的对比分析
- 是否有结构化的对比表格（功能矩阵、定价对比等）
- 是否包含 SWOT 分析和具体的战略建议
- 报告格式为 Markdown，可直接渲染
