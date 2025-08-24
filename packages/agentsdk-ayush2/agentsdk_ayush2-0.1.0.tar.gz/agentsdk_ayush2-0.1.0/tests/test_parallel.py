from __future__ import annotations

import time
from typing import Dict

from agentsdk.state import SessionManager
from agentsdk.tool_subsystem import ToolRegistry
from agentsdk.agent import Agent
from agentsdk.orchestration import OrchestratorAgent
from agentsdk.tools.ShellTool import ShellTool


def test_parallel_subagents_sleep(tmp_path) -> None:
    sessions = SessionManager()
    registry = ToolRegistry()
    registry.register(ShellTool(root=tmp_path))

    # Bedrock client not used when running explicit tool plan; agent is required but won't call LLM
    class NoBedrock:  # minimal placeholder; not used
        pass

    base_agent = Agent(
        name="default",
        bedrock=NoBedrock(),  # type: ignore[arg-type]
        registry=registry,
        sessions=sessions,
        system_prompt=None,
    )

    orchestrator = OrchestratorAgent(
        planner=base_agent,
        sub_agents={"sh1": base_agent, "sh2": base_agent},
        sessions=sessions,
        max_parallel=4,
    )

    plan = [
        {"task_id": "a", "description": "sleep 2", "agent": "sh1", "tool": "shell", "args": {"command": "sleep 2"}},
        {"task_id": "b", "description": "sleep 2", "agent": "sh2", "tool": "shell", "args": {"command": "sleep 2"}},
    ]

    t0 = time.perf_counter()
    _ = orchestrator.run(session_id="s-par", query="", plan=plan, synthesize=False)
    dt = time.perf_counter() - t0

    # If executed in parallel, total should be close to ~2s, well below 4s
    assert dt < 3.5, f"Expected parallel execution (<3.5s), got {dt:.2f}s"


