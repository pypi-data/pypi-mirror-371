from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class ToolError(Exception):
    """Raised when a tool fails or receives invalid input."""


class BaseTool(ABC):
    """Abstract base class for all tools in the SDK."""

    name: str
    description: str
    input_schema: Dict[str, Any]

    @abstractmethod
    def run(self, **kwargs: Any) -> str:
        """Execute the tool with validated kwargs and return a string result."""

    def tool_config(self) -> Dict[str, Any]:
        """Return Bedrock tool configuration for this tool."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        }


@dataclass
class RegisteredTool:
    name: str
    tool: BaseTool


class ToolRegistry:
    """Registry for tools; supports registration, config export, and execution."""

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def is_registered(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> List[str]:
        return sorted(self._tools.keys())

    def tool_configs(self, allowed_tools: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        names = allowed_tools if allowed_tools is not None else self.list_tools()
        configs: List[Dict[str, Any]] = []
        for name in names:
            tool = self._tools.get(name)
            if tool is not None:
                configs.append(tool.tool_config())
        return configs

    def run_tool(self, name: str, **kwargs: Any) -> str:
        tool = self._tools.get(name)
        if tool is None:
            raise ToolError(f"Unknown tool: {name}")
        try:
            return tool.run(**kwargs)
        except ToolError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise ToolError(f"Tool '{name}' failed: {exc}") from exc


