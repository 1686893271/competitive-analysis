# CrewAI 竞品分析项目架构分析

> 分析时间：2025-07-09
> 分析人：Hermes (spaceclaw)

---

## 一、整体架构

```
main.py (入口)
    ↓
CompetitiveAnalysisCrew (crew.py)
    ├── 3个 Agent（agents.yaml）
    │   ├── market_researcher     → 调研专家
    │   ├── product_analyst       → 产品分析专家
    │   └── strategy_advisor      → 战略顾问
    │
    ├── 3个 Task（tasks.yaml）
    │   ├── research_task     → 市场调研
    │   ├── analysis_task     → 产品对比
    │   └── report_task       → 整合报告
    │
    └── Process.sequential（顺序执行）
        调研 → 分析 → 报告（链式传递，上一任务输出给下一任务）
```

---

## 二、执行流程图

```
[research_task]          [analysis_task]           [report_task]
 市场调研专家               产品分析专家               战略顾问
     ↓                        ↓                        ↓
 行业规模/竞品数据        产品功能/定价/体验         整合最终报告
     ↓                        ↓                        ↓
  ─────────────────────────────────────────────────────→↓
                                               输出到:
                                         competitive_analysis_report.md
```

---

## 三、Agent 职责

| Agent | Role | 核心任务 | 输出 |
|---|---|---|---|
| `market_researcher` | 行业调研专家 | 市场规模、竞品格局、技术趋势 | 市场调研报告 |
| `product_analyst` | 产品对比专家 | 功能矩阵、定价、用户体验、SWOT | 产品分析报告 |
| `strategy_advisor` | 战略顾问 | 综合前两者，输出可执行建议 | 完整 Markdown 报告 |

---

## 四、Agent 配置（agents.yaml）

```yaml
market_researcher:
  role: "{industry} 行业市场调研专家"
  goal: "深入调研 {company} 在 {industry} 行业中的竞争格局"
  backstory: "资深行业分析师，10年+市场研究经验，数据驱动，逻辑清晰"

product_analyst:
  role: "产品功能对比分析专家"
  goal: "对 {company} 及其主要竞品进行深度产品功能对比分析"
  backstory: "产品经理转型分析师，敏锐洞察力，用户视角，结构化分析"

strategy_advisor:
  role: "战略建议与报告撰写专家"
  goal: "基于调研和分析结果，撰写完整竞品分析报告并提出战略建议"
  backstory: "顶级管理咨询顾问，多家咨询公司任职，逻辑严密，建议可执行"
```

---

## 五、Task 配置（tasks.yaml）

### research_task（市场调研）
- 分析行业整体市场规模、增长趋势、关键驱动因素
- 识别主要竞争对手（至少 3-5 家）
- 收集竞品核心数据：市场份额、融资、用户规模、核心产品
- 分析技术发展趋势
- 总结公司在行业中的竞争地位
- **输出**：结构化市场调研报告（含行业概览、竞争格局图谱、数据对比表）

### analysis_task（产品对比）
- 分析各竞品核心产品功能列表
- 对比技术架构和实现方案
- 分析目标用户群体和定价策略
- 评估用户体验和口碑
- 识别竞争优势和改进方向
- **输出**：详细产品功能对比报告（含对比矩阵、SWOT）

### report_task（整合报告）
- 综合前两者，撰写完整报告
- 执行摘要、行业概况、竞品分析、SWOT、战略建议（短/中/长期）
- **输出**：`competitive_analysis_report.md`

---

## 六、代码结构

```
src/competitive_analysis/
├── main.py              # 入口，参数解析 + kickoff
├── crew.py              # CrewAI @CrewBase 定义，LLM 配置
├── __init__.py
├── config/
│   ├── agents.yaml      # 3个 Agent 的 role/goal/backstory
│   └── tasks.yaml       # 3个 Task 的 description/expected_output
└── tools/
    └── __init__.py      # 空目录，无自定义工具
```

---

## 七、CrewAI 框架使用方式

### LLM 配置（crew.py）
```python
llm=LLM(
    model="MiniMax-M2.7",
    base_url="https://api.minimaxi.com/v1",
    api_key=os.environ.get("MINIMAX_API_KEY", ""),
)
```

### 执行方式
```python
result = CompetitiveAnalysisCrew().crew().kickoff(
    inputs={'company': 'OpenAI', 'industry': '大语言模型'}
)
```

### 关键特性
- **配置驱动**：Agent/Task 描述全在 YAML，代码是框架
- **变量注入**： `{company}` 和 `{industry}` 在 kickoff 时通过 inputs 注入
- **顺序执行**：Process.sequential，任务链式传递

---

## 八、与 Hermes 原生 Skill 的核心区别

| | CrewAI 项目 | Hermes 原生 Skill |
|---|---|---|
| **执行模式** | 独立 Python 进程 + 外部 LLM API | 在 Hermes 进程内直接调用 |
| **Agent 定义** | YAML 配置 + `@CrewBase` 装饰器 | SKILL.md 里的 prompt + 工具 |
| **任务编排** | CrewAI 框架的 `Process.sequential` | cronjob / delegate_task / prompt chain |
| **工具调用** | 无自定义工具（tools/ 是空目录） | Hermes 工具集（browser/search/file/...） |
| **输出** | 写本地 Markdown 文件 | 直接发飞书/保存本地 |
| **依赖** | crewai、litellm、openai 包 | 无额外依赖 |

---

## 九、已知问题

### 1. API Key 认证失败（401）
- **症状**：`login fail: Please carry the API secret key in the 'Authorization' field`
- **根因**：`.env` 里的 `MINIMAX_API_KEY` 是占位符 `${MINI...KEY}`，不是真实 key
- **真实 key** 在 `~/.hermes/config.yaml` 里，`sk-cp-` 前缀
- **修复**：把 config.yaml 里的 key 写入 `.env`

### 2. Key 类型限制
- `sk-cp-`（Coding Plan）：文本生成 OK，图片理解失败
- `sk-token-`（Token Plan）：图片理解 + 代码补全

### 3. 无自定义工具
- `tools/` 目录是空的，Agent 只能靠自身知识
- 无法实时抓取竞品数据，报告依赖训练知识（可能过时）

### 4. 执行超时
- 完整流程（调研→分析→报告）需要 5 分钟以上
- terminal() 默认 timeout 较短，需设置更大值

### 5. 顺序执行瓶颈
- 3 个 Task 串行，analysis 需等 research 完成
- 无法并行化处理独立环节

---

## 十、改造方向建议

### 方案 A（轻量，保持现状）
保留 CrewAI 项目作为 `terminal()` 调用的脚本，Hermes Skill 只负责传参和展示结果。

**优点**：快速可用，改动小
**缺点**：仍依赖外部进程和 CrewAI 包

### 方案 B（原生 Hermes Skill）
用 Hermes 原生能力替代 CrewAI：
- 用 `web_search` / `browser` 工具做实时调研
- 用 prompt chain 做分析
- 用 `feishu-send-message` 发报告
- 去掉 CrewAI 依赖

**优点**：架构更简洁，无额外依赖，可利用 Hermes 全部工具
**缺点**：需要较大改写，prompt 工程量大

### 方案 C（混合架构）
保留 CrewAI 的 Agent 设计思路，但接入 Hermes 工具：
- Agent prompt 里引导调用 Hermes 工具（browser/search）
- 用 `delegate_task` 在子 agent 里使用工具
- 报告生成后通过 feishu 发出

**优点**：结合两者优势
**缺点**：CrewAI 和 Hermes 工具集集成需要开发工作

---

## 十一、文件依赖关系

```
main.py
  └── from competitive_analysis.crew import CompetitiveAnalysisCrew
        └── CompetitiveAnalysisCrew (crew.py, @CrewBase)
              ├── agents_config['market_researcher'] → config/agents.yaml
              ├── agents_config['product_analyst']   → config/agents.yaml
              ├── agents_config['strategy_advisor']  → config/agents.yaml
              ├── tasks_config['research_task']      → config/tasks.yaml
              ├── tasks_config['analysis_task']      → config/tasks.yaml
              └── tasks_config['report_task']        → config/tasks.yaml
```

---

## 十二、运行日志摘要（OpenAI 大语言模型行业分析）

研究任务成功执行，生成约 85KB 的报告内容，包含：

- **行业概览**：全球 LLM 市场规模 2025 年预计 280-350 亿美元
- **竞争格局**：OpenAI/Google DeepMind/Anthropic/Meta/国内厂商分层
- **竞品数据**：各厂商估值、融资、用户规模、核心产品对比
- **技术趋势**：多模态、Agent、推理能力、MoE 架构
- **OpenAI SWOT**：优势（技术/品牌/生态）vs 劣势（亏损/竞争/人才流失）
- **战略建议**：短中长期策略建议

分析任务和报告任务因超时未能完成完整流程。
