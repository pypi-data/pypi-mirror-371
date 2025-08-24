from __future__ import annotations

import os
import uuid
import click

from agentsdk.aws import BedrockClient
from agentsdk.tool_subsystem import ToolRegistry
from agentsdk.state import SessionManager
from agentsdk.agent import Agent
from agentsdk.orchestration import OrchestratorAgent, load_sub_agents_from_dir, scaffold_sub_agent_yaml
from agentsdk.tools.FileSystemTool import FileSystemTool
from agentsdk.tools.ShellTool import ShellTool
from agentsdk.tools.WebSearchTool import WebFetchTool


@click.group()
def main() -> None:
    pass


@main.command("run")
@click.option("--model-id", required=False, default="openai.gpt-oss-120b-1:0", help="Bedrock model ID")
@click.option("--region", required=False, default="us-west-2", help="AWS region name")
@click.option("--query", required=True, help="User query/task")
@click.option("--agents-dir", required=False, default=".agents", help="Directory containing sub-agent configs")
@click.option("--show-thoughts/--no-show-thoughts", default=True, help="Print agent and sub-agent lifecycle events")
def run_cmd(model_id: str, region: str | None, query: str, agents_dir: str, show_thoughts: bool) -> None:
    sessions = SessionManager()
    bedrock = BedrockClient(model_id=model_id, region_name=region)
    registry = ToolRegistry()
    registry.register(FileSystemTool(root=os.getcwd()))
    registry.register(ShellTool(root=os.getcwd()))
    registry.register(WebFetchTool())

    # Base default agent
    def on_thought(agent_name: str, kind: str, text: str) -> None:
        if show_thoughts:
            click.echo(f"[{agent_name}][{kind}] {text[:200]}")

    default_agent = Agent(
        name="default",
        bedrock=bedrock,
        registry=registry,
        sessions=sessions,
        system_prompt="You are a helpful coding assistant with access to tools.",
        on_thought=on_thought,
    )

    sub_agents = load_sub_agents_from_dir(directory=os.path.join(os.getcwd(), agents_dir), base_agent=default_agent)

    def on_start(agent_name: str, task_id: str) -> None:
        if show_thoughts:
            click.echo(f"[start] agent={agent_name} task={task_id}")

    def on_end(agent_name: str, task_id: str, output: str) -> None:
        if show_thoughts:
            click.echo(f"[end] agent={agent_name} task={task_id}\n{output[:400]}".rstrip())

    orchestrator = OrchestratorAgent(
        planner=default_agent,
        sub_agents=sub_agents,
        sessions=sessions,
        on_subagent_start=on_start,
        on_subagent_end=on_end,
    )

    session_id = str(uuid.uuid4())
    result = orchestrator.run(session_id=session_id, query=query)
    click.echo(result)


@main.command("init-agent")
@click.option("--agents-dir", required=False, default=".agents", help="Directory to write agent YAML")
@click.option("--name", required=True, help="Sub-agent name")
@click.option("--instructions", required=True, help="System instructions for sub-agent")
@click.option("--tools", required=False, multiple=True, help="Allowed tools (repeat flag)")
def init_agent(agents_dir: str, name: str, instructions: str, tools: tuple[str, ...]) -> None:
    path = scaffold_sub_agent_yaml(agents_dir, name, instructions, list(tools) if tools else None)
    click.echo(f"Created {path}")


if __name__ == "__main__":
    main()


