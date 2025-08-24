from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from agentsdk.tool_subsystem import BaseTool, ToolError


class FileSystemTool(BaseTool):
    name = "file_system"
    description = "Read, write, and list files within the workspace sandbox."
    input_schema = {
        "type": "object",
        "properties": {
            "operation": {"type": "string", "enum": ["read", "write", "list"]},
            "path": {"type": "string"},
            "content": {"type": "string"},
        },
        "required": ["operation", "path"],
        "additionalProperties": False,
    }

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    def _resolve_safe(self, rel_path: str | Path) -> Path:
        candidate = (self.root / Path(rel_path)).resolve()
        if not str(candidate).startswith(str(self.root)):
            raise ToolError("Access outside sandbox is prohibited")
        return candidate

    def run(self, **kwargs: Any) -> str:
        op = kwargs.get("operation")
        rel_path = kwargs.get("path")
        content = kwargs.get("content")
        if op not in {"read", "write", "list"}:
            raise ToolError("Unsupported operation")
        if not isinstance(rel_path, str):
            raise ToolError("'path' must be a string")
        path = self._resolve_safe(rel_path)

        if op == "read":
            if not path.exists() or not path.is_file():
                raise ToolError("File not found")
            return path.read_text(encoding="utf-8")

        if op == "write":
            if content is None or not isinstance(content, str):
                raise ToolError("'content' required for write")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return "OK"

        # list
        if not path.exists() or not path.is_dir():
            raise ToolError("Directory not found")
        entries = sorted(p.name for p in path.iterdir())
        return "\n".join(entries)


