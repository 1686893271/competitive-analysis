from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List
from crewai.agents.agent_builder.base_agent import BaseAgent


@CrewBase
class CompetitiveAnalysisCrew():
    """多 Agent 竞品分析报告生成系统

    架构说明：
    - 3 个专业化 Agent 角色：市场调研专家、产品分析师、战略顾问
    - 采用顺序执行流程 (Sequential Process)，任务链式传递
    - 每个 Agent 基于前一个 Agent 的输出进行深度加工
    - 最终输出完整的 Markdown 格式竞品分析报告
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['market_researcher'],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def product_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['product_analyst'],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def strategy_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['strategy_advisor'],
            verbose=True,
            allow_delegation=False,
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
        )

    @task
    def report_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_task'],
            output_file='competitive_analysis_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """创建竞品分析 Crew

        执行模式：顺序流程
        调研 → 分析 → 报告
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
