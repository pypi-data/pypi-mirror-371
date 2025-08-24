from __future__ import annotations

from typing import Any, Dict, List

from agentsdk.agent import Agent
from agentsdk.state import SessionManager
from agentsdk.tool_subsystem import ToolRegistry
from agentsdk.orchestration import OrchestratorAgent


class DummyBedrock:
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    def invoke(self, messages: List[Dict[str, Any]], system=None, tools=None, tool_choice=None, temperature=None, max_tokens=None, metadata=None):  # noqa: D401, ANN001
        # Simple echo model: return latest user text
        self.calls.append({"messages": messages, "system": system})
        content = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                blocks = m.get("content") or []
                for b in blocks:
                    if b.get("type") == "text":
                        content = b.get("text", "")
                        break
                if content:
                    break
        return {"content": [{"type": "text", "text": content }]}


def test_orchestrator_parallel() -> None:
    sessions = SessionManager()
    bedrock = DummyBedrock()
    registry = ToolRegistry()
    base_agent = Agent(name="default", bedrock=bedrock, registry=registry, sessions=sessions)
    orchestrator = OrchestratorAgent(planner=base_agent, sub_agents={"default": base_agent}, sessions=sessions)
    output = orchestrator.run(session_id="s1", query="hello world")
    assert "hello world" in output


