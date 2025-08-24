from __future__ import annotations

import os
from typing import Any

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

from agentsdk.tool_subsystem import BaseTool, ToolError


class WebFetchTool(BaseTool):
    name = "web_fetch"
    description = "Fetch a URL over HTTP(S). Disabled unless ALLOW_NETWORK=true."
    input_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string"},
            "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 30},
        },
        "required": ["url"],
        "additionalProperties": False,
    }

    def run(self, **kwargs: Any) -> str:
        if os.getenv("ALLOW_NETWORK", "false").lower() not in {"1", "true", "yes"}:
            raise ToolError("Networking disabled. Set ALLOW_NETWORK=true to enable.")
        if requests is None:
            raise ToolError("'requests' not installed")
        url = kwargs.get("url")
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise ToolError("Invalid 'url'")
        timeout_seconds = int(kwargs.get("timeout_seconds", 10))
        try:
            resp = requests.get(url, timeout=timeout_seconds, headers={"User-Agent": "AgentSDK/1.0"})
            resp.raise_for_status()
            text = resp.text
            if len(text) > 20000:
                text = text[:20000] + "\n...[truncated]"
            return text
        except Exception as exc:  # noqa: BLE001
            raise ToolError(f"Fetch failed: {exc}") from exc


