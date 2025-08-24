from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import Any

from agentsdk.tool_subsystem import BaseTool, ToolError


class ShellTool(BaseTool):
    name = "shell"
    description = "Execute shell commands in a sandboxed working directory."
    input_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string"},
            "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 300},
            "cwd": {"type": "string"},
        },
        "required": ["command"],
        "additionalProperties": False,
    }

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    def _resolve_safe(self, rel_path: str | None) -> Path:
        path = self.root if not rel_path else (self.root / rel_path)
        resolved = path.resolve()
        if not str(resolved).startswith(str(self.root)):
            raise ToolError("Access outside sandbox is prohibited")
        return resolved

    def run(self, **kwargs: Any) -> str:
        command = kwargs.get("command")
        if not isinstance(command, str) or not command.strip():
            raise ToolError("'command' must be a non-empty string")
        timeout_seconds = kwargs.get("timeout_seconds", 60)
        cwd = self._resolve_safe(kwargs.get("cwd"))

        try:
            completed = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=int(timeout_seconds),
                env={"PATH": os.getenv("PATH", ""), "HOME": os.getenv("HOME", ""), "LANG": "C"},
                text=True,
            )
        except subprocess.TimeoutExpired as exc:
            raise ToolError(f"Command timed out after {timeout_seconds}s") from exc
        except Exception as exc:  # noqa: BLE001
            raise ToolError(f"Failed to execute command: {exc}") from exc

        output = completed.stdout
        if completed.returncode != 0:
            output += ("\n" if output else "") + f"[exit {completed.returncode}]\n" + completed.stderr
        return output.strip()


