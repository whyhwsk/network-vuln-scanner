from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent

from network_vuln_scanner.tools.custom_tool import NmapFullScanTool, SnmpEnumTool, SshAuditTool

deepseek_llm = LLM(model="deepseek/deepseek-chat", timeout=180, max_retries=2)
deepseek_reasoner_llm = LLM(model="deepseek/deepseek-reasoner", timeout=300, max_retries=2)


@CrewBase
class NetworkVulnScanner():
    """NetworkVulnScanner crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def network_scanner(self) -> Agent:
        return Agent(
            config=self.agents_config['network_scanner'], # type: ignore[index]
            tools=[NmapFullScanTool(), SnmpEnumTool(), SshAuditTool()],
            llm=deepseek_llm,
            verbose=True
        )

    @agent
    def report_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['report_analyst'], # type: ignore[index]
            llm=deepseek_reasoner_llm,
            verbose=True
        )

    @task
    def scan_task(self) -> Task:
        return Task(
            config=self.tasks_config['scan_task'], # type: ignore[index]
        )

    @task
    def report_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_task'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the NetworkVulnScanner crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
