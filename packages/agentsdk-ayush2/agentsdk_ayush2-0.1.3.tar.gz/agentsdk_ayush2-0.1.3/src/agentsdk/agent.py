from __future__ import annotations

from typing import Any, Dict, List, Optional, Callable
import json

from agentsdk.aws import BedrockClient
from agentsdk.state import SessionManager
from agentsdk.tool_subsystem import ToolRegistry, ToolError


def _to_anthropic_blocks(text: str) -> List[Dict[str, Any]]:
    return [{"type": "text", "text": text}]


def _extract_content_blocks(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Be tolerant of structural variations
    if isinstance(response.get("content"), list):
        return response["content"]
    if isinstance(response.get("output"), dict) and isinstance(response["output"].get("content"), list):
        return response["output"]["content"]
    if isinstance(response.get("message"), dict) and isinstance(response["message"].get("content"), list):
        return response["message"]["content"]
    # OpenAI-style: choices -> message -> content (string)
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        msg = choices[0].get("message", {})
        tool_calls = msg.get("tool_calls") or []
        blocks: List[Dict[str, Any]] = []
        for call in tool_calls:
            if call.get("type") == "function":
                fn = call.get("function", {})
                raw_args = fn.get("arguments")
                parsed_input: Dict[str, Any] = {}
                if isinstance(raw_args, str):
                    try:
                        tmp = json.loads(raw_args)
                        if isinstance(tmp, dict):
                            parsed_input = tmp
                        elif isinstance(tmp, list) and tmp and isinstance(tmp[0], dict):
                            parsed_input = tmp[0]
                        else:
                            parsed_input = {"args": tmp}
                    except Exception:
                        parsed_input = {}
                elif isinstance(raw_args, dict):
                    parsed_input = raw_args
                else:
                    parsed_input = {}
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": call.get("id"),
                        "name": fn.get("name"),
                        "input": parsed_input,
                    }
                )
        text = msg.get("content", "")
        if isinstance(text, str) and text:
            blocks.insert(0, {"type": "text", "text": text})
        return blocks
    return []


class Agent:
    """Base Agent implementing a ReAct loop with Bedrock tool-use."""

    def __init__(
        self,
        name: str,
        bedrock: BedrockClient,
        registry: ToolRegistry,
        sessions: SessionManager,
        system_prompt: Optional[str] = None,
        max_turns: int = 15,
        allowed_tools: Optional[List[str]] = None,
        on_thought: Optional[Callable[[str, str, str], None]] = None,
    ) -> None:
        self.name = name
        self.bedrock = bedrock
        self.registry = registry
        self.sessions = sessions
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self.allowed_tools = allowed_tools
        self.on_thought = on_thought

    def chat(self, session_id: str, user_input: str) -> str:
        self.sessions.append_message(session_id, role="user", content=user_input)
        final_text = ""

        for _ in range(self.max_turns):
            messages = [
                {"role": m.role, "content": _to_anthropic_blocks(m.content)}
                for m in self.sessions.get_messages(session_id)
            ]

            tools = self.registry.tool_configs(self.allowed_tools)
            response = self.bedrock.invoke(
                messages=messages,
                system=self.system_prompt,
                tools=tools if tools else None,
            )

            content_blocks = _extract_content_blocks(response)
            if not content_blocks:
                # Fallback: no content; stop
                break

            any_tool_use = False
            aggregated_text: List[str] = []

            for block in content_blocks:
                btype = block.get("type")
                if btype == "text":
                    text = block.get("text", "")
                    if text:
                        aggregated_text.append(text)
                        if self.on_thought:
                            try:
                                self.on_thought(self.name, "thought", text)
                            except Exception:
                                pass
                elif btype == "tool_use":
                    any_tool_use = True
                    tool_name = block.get("name")
                    tool_input = block.get("input", {})
                    tool_use_id = block.get("id")
                    try:
                        result = self.registry.run_tool(tool_name, **tool_input)
                    except ToolError as exc:
                        result = f"TOOL_ERROR: {exc}"

                    # Append tool_result for the next turn
                    # Record tool result for next turn as a user message
                    self.sessions.append_message(session_id, role="user", content=str(result))
                    if self.on_thought:
                        try:
                            self.on_thought(self.name, "tool_result", str(result))
                        except Exception:
                            pass

            if aggregated_text:
                final_text = "\n".join(aggregated_text)
                self.sessions.append_message(session_id, role="assistant", content=final_text)

            if not any_tool_use:
                break

        return final_text


