from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable

import concurrent.futures

from agentsdk.agent import Agent
from agentsdk.state import SessionManager
from agentsdk.tool_subsystem import ToolRegistry

try:
    import frontmatter  # type: ignore
except Exception:  # pragma: no cover
    frontmatter = None  # type: ignore
from pathlib import Path
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore


@dataclass
class SubAgentConfig:
    name: str
    description: str
    tools: Optional[List[str]] = None
    system_prompt: Optional[str] = None


class OrchestratorAgent:
    """Orchestrates task decomposition and parallel sub-agent execution."""

    def __init__(
        self,
        planner: Agent,
        sub_agents: Dict[str, Agent],
        sessions: SessionManager,
        max_parallel: int = 4,
        on_subagent_start: Optional[Callable[[str, str], None]] = None,
        on_subagent_end: Optional[Callable[[str, str, str], None]] = None,
    ) -> None:
        self.planner = planner
        self.sub_agents = sub_agents
        self.sessions = sessions
        self.max_parallel = max_parallel
        self.on_subagent_start = on_subagent_start
        self.on_subagent_end = on_subagent_end

    def decompose(self, session_id: str, query: str) -> List[Dict[str, Any]]:
        # Build a planning prompt that enumerates available sub-agents
        agent_list = []
        name_list: List[str] = []
        for k, a in self.sub_agents.items():
            if k == "default":
                continue
            agent_list.append({"name": k, "tools": a.allowed_tools or []})
            name_list.append(k)
        example = [
            {
                "task_id": "research",
                "description": "Research best practices and provide citations.",
                "agent": (name_list[0] if name_list else "default"),
                "inputs": query,
            },
            {
                "task_id": "audit",
                "description": "Audit the repository for secrets and risky configs.",
                "agent": (name_list[1] if len(name_list) > 1 else (name_list[0] if name_list else "default")),
                "inputs": query,
            },
        ]
        plan_prompt = (
            "You are the orchestrator. Plan tasks using AVAILABLE SUB-AGENTS.\n"
            "OUTPUT FORMAT (MANDATORY): Return ONLY a JSON ARRAY (no keys/wrappers).\n"
            "ITEM SCHEMA (MANDATORY keys): {task_id: string, description: string, agent: string, inputs: string}.\n"
            "agent MUST be EXACTLY one of: " + ", ".join(name_list) + ". Use AT LEAST TWO distinct agents when possible; prefer parallel tasks.\n"
            f"Available agents with allowed tools (for your reference): {agent_list}\n"
            f"EXAMPLE (follow structure, not content): {example}"
        )
        system = (self.planner.system_prompt or "") + "\n\n" + plan_prompt
        planner = Agent(
            name=self.planner.name,
            bedrock=self.planner.bedrock,
            registry=self.planner.registry,
            sessions=self.sessions,
            system_prompt=system,
            max_turns=3,
        )
        text = planner.chat(session_id=session_id + ":plan", user_input=query)

        import json
        def try_parse_tasks(txt: str) -> Optional[List[Dict[str, Any]]]:
            try:
                data = json.loads(txt)
            except Exception:
                return None
            tasks = None
            if isinstance(data, list):
                tasks = data
            elif isinstance(data, dict) and isinstance(data.get("plan"), list):
                tasks = data.get("plan")
            if tasks is None:
                return None
            valid_names = {k for k in self.sub_agents.keys() if k != "default"}
            def normalize(name: str) -> str:
                raw = str(name).strip()
                if raw in valid_names:
                    return raw
                lowered_map = {n.lower(): n for n in valid_names}
                if raw.lower() in lowered_map:
                    return lowered_map[raw.lower()]
                candidate = raw.lower().replace(" ", "-")
                synonyms = {
                    "research": "researcher",
                    "web": "researcher",
                    "audit": "security-auditor",
                    "security": "security-auditor",
                    "refactor": "code-refactorer",
                    "refactorer": "code-refactorer",
                    "test": "test-writer",
                    "tests": "test-writer",
                }
                for key, target in synonyms.items():
                    if key in candidate and target in valid_names:
                        return target
                return "default"

            cleaned: List[Dict[str, Any]] = []
            for item in tasks:
                if not isinstance(item, dict):
                    continue
                # accept alternative keys (task -> description)
                desc = item.get("description") or item.get("task") or ""
                tid = str(item.get("task_id") or (desc[:12] or "t")).replace(" ", "-")
                agent_name = normalize(str(item.get("agent") or "default"))
                inputs = str(item.get("inputs") or desc)
                cleaned.append({
                    "task_id": tid,
                    "description": str(desc),
                    "agent": agent_name,
                    "inputs": inputs,
                })
            # Ensure at least two distinct agents when possible
            distinct_agents = {t["agent"] for t in cleaned if t["agent"] != "default"}
            if len(distinct_agents) < 2 and name_list:
                needed = [n for n in name_list if n not in distinct_agents]
                for miss in needed[: max(0, 2 - len(distinct_agents))]:
                    cleaned.append({
                        "task_id": f"auto-{miss}",
                        "description": f"Auto-task for {miss} based on user goal",
                        "agent": miss,
                        "inputs": query,
                    })
            return cleaned or None

        # Try parse, then single retry with a stricter nudge, then synthesize fallback
        parsed_tasks = try_parse_tasks(text)
        if not parsed_tasks:
            nudge = (
                "Return ONLY a JSON array. Keys per item: task_id, description, agent (one of: "
                + ", ".join(name_list)
                + "), inputs. Use >=2 distinct agents."
            )
            text = planner.chat(session_id=session_id + ":plan-retry", user_input=nudge)
            parsed_tasks = try_parse_tasks(text)
        if parsed_tasks:
            return parsed_tasks

        # Programmatic synthesis fallback to ensure parallel work
        fallback: List[Dict[str, Any]] = []
        for idx, agent_name in enumerate(name_list[: max(2, min(3, len(name_list)))]):
            fallback.append({
                "task_id": f"auto-{idx+1}-{agent_name}",
                "description": f"Auto-generated task for {agent_name} based on user goal.",
                "agent": agent_name,
                "inputs": query,
            })
        if fallback:
            return fallback
        # Fallback to single task
        return [{"task_id": "t1", "description": query, "agent": "default", "inputs": query}]

    def run(self, session_id: str, query: str, plan: Optional[List[Dict[str, Any]]] = None, *, synthesize: bool = True) -> str:
        plan = plan or self.decompose(session_id, query)

        results: Dict[str, str] = {}
        futures: List[concurrent.futures.Future[str]] = []
        future_to_info: Dict[concurrent.futures.Future[str], Dict[str, str]] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            for item in plan:
                agent_key = item.get("agent") or "default"
                agent = self.sub_agents.get(agent_key) or self.sub_agents.get("default")
                if agent is None:
                    continue
                task_input = item.get("inputs") or item.get("description") or query
                if self.on_subagent_start:
                    try:
                        self.on_subagent_start(agent_key, str(item.get("task_id", "t")))
                    except Exception:
                        pass
                # If explicit tool is provided, run the tool directly
                tool_name = item.get("tool")
                tool_args = item.get("args") or {}
                if tool_name:
                    # Use the agent's registry
                    registry: ToolRegistry = agent.registry
                    fut = executor.submit(lambda: registry.run_tool(tool_name, **tool_args))
                else:
                    # Build a delegatory system addendum to preserve base template while adding task context
                    delegatory = (
                        "[Delegation]\n"
                        f"Task ID: {item.get('task_id','t')}\n"
                        f"Objective: {task_input}\n"
                        f"Allowed tools: {agent.allowed_tools or 'inherited'}\n"
                        "Output: Be concise and directly actionable."
                    )
                    fut = executor.submit(
                        agent.chat,
                        session_id=f"{session_id}:{item.get('task_id','t')}\n",
                        user_input=str(task_input),
                        system_addendum=delegatory,
                    )
                futures.append(fut)
                future_to_info[fut] = {"agent": agent_key, "task_id": str(item.get("task_id", "t"))}

            for idx, fut in enumerate(concurrent.futures.as_completed(futures), start=1):
                try:
                    out = fut.result()
                    results[str(idx)] = out
                except Exception as exc:  # noqa: BLE001
                    out = f"ERROR: {exc}"
                    results[str(idx)] = out
                if self.on_subagent_end:
                    try:
                        info = future_to_info.get(fut, {"agent": "unknown", "task_id": str(idx)})
                        self.on_subagent_end(info["agent"], info["task_id"], out)
                    except Exception:
                        pass

        if not synthesize:
            return "\n\n".join(v for _, v in sorted(results.items(), key=lambda kv: kv[0]))

        # Synthesis step: LLM consolidation using the planner
        synthesis_prompt = (
            "You are a synthesis agent. Combine the following task results into a concise, actionable answer.\n"
            "Ensure correctness, remove duplication, and provide clear next steps if relevant.\n\n"
        )
        parts = []
        for key, value in sorted(results.items(), key=lambda kv: kv[0]):
            parts.append(f"Task {key}:\n{value}")
        synthesis_input = synthesis_prompt + "\n\n" + "\n\n".join(parts)

        final_text = self.planner.chat(session_id=f"{session_id}:synthesis", user_input=synthesis_input)
        return final_text or "\n\n".join(v for _, v in sorted(results.items(), key=lambda kv: kv[0]))


def load_sub_agents_from_dir(
    directory: str | Path,
    base_agent: Agent,
) -> Dict[str, Agent]:
    """Load sub-agent configs from Markdown (YAML frontmatter) and YAML files."""
    agents: Dict[str, Agent] = {"default": base_agent}
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        return agents
    # Load Markdown configs
    if frontmatter is not None:
        for md_file in dir_path.glob("*.md"):
            try:
                post = frontmatter.load(md_file)
                meta = post.metadata or {}
                name = str(meta.get("name") or md_file.stem)
                tools = meta.get("tools")
                if tools is not None and not isinstance(tools, list):
                    tools = None
                system_prompt = str(post.content or "")
                sub_agent = Agent(
                    name=name,
                    bedrock=base_agent.bedrock,
                    registry=base_agent.registry,
                    sessions=base_agent.sessions,
                    system_prompt=system_prompt,
                    max_turns=base_agent.max_turns,
                    allowed_tools=tools,
                    on_thought=base_agent.on_thought,
                )
                agents[name] = sub_agent
            except Exception:
                continue
    # Load YAML configs
    if yaml is not None:
        for yml in list(dir_path.glob("*.yml")) + list(dir_path.glob("*.yaml")):
            try:
                data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
                name = str(data.get("name") or yml.stem)
                system_prompt = str(data.get("system") or data.get("instructions") or "")
                tools = data.get("tools")
                if tools is not None and not isinstance(tools, list):
                    tools = None
                sub_agent = Agent(
                    name=name,
                    bedrock=base_agent.bedrock,
                    registry=base_agent.registry,
                    sessions=base_agent.sessions,
                    system_prompt=system_prompt,
                    max_turns=base_agent.max_turns,
                    allowed_tools=tools,
                    on_thought=base_agent.on_thought,
                )
                agents[name] = sub_agent
            except Exception:
                continue
    return agents


def scaffold_sub_agent_yaml(
    target_dir: str | Path,
    name: str,
    instructions: str,
    tools: Optional[List[str]] = None,
) -> Path:
    """Create a YAML sub-agent config file with the provided parameters."""
    path = Path(target_dir)
    path.mkdir(parents=True, exist_ok=True)
    filename = path / f"{name}.yaml"
    data = {
        "name": name,
        "instructions": instructions,
        "tools": tools or ["file_system"],
    }
    if yaml is None:
        # Minimal manual YAML
        content = (
            f"name: {name}\n"
            f"instructions: |\n  " + instructions.replace("\n", "\n  ") + "\n"
            f"tools: {data['tools']}\n"
        )
        filename.write_text(content, encoding="utf-8")
    else:
        filename.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return filename


