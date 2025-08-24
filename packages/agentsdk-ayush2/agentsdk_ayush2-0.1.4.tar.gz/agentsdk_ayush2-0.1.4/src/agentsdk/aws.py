from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import importlib
import json
import time


@dataclass
class BedrockMessage:
    role: str
    content: str


class BedrockClient:
    """
    Thin wrapper around AWS Bedrock Runtime client for Claude models.

    Provides a simple interface for tool-augmented chat completions and basic retries.
    """

    def __init__(
        self,
        model_id: str,
        region_name: Optional[str] = None,
        timeout_seconds: int = 60,
        max_retries: int = 3,
        user_agent_extra: str = "AgentSDK/BedrockClient",
    ) -> None:
        self.model_id = model_id
        # Lazy import heavy AWS SDK modules to avoid import-time OpenSSL issues in test envs
        boto3 = importlib.import_module("boto3")
        botocore_config = importlib.import_module("botocore.config")
        Config = getattr(botocore_config, "Config")
        config = Config(
            region_name=region_name,
            retries={"max_attempts": max_retries, "mode": "standard"},
            user_agent_extra=user_agent_extra,
            read_timeout=timeout_seconds,
            connect_timeout=timeout_seconds,
        )
        self._client = boto3.client("bedrock-runtime", config=config)
        self._max_retries = max_retries

    def invoke(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke Claude via Bedrock Runtime with messages and optional tool configuration.

        Args:
            messages: Anthropic-style message list.
            system: Optional system prompt string.
            tools: Optional tool configuration list per Bedrock tool-use schema.
            tool_choice: Optional tool selection directive.
            temperature: Optional generation temperature.
            max_tokens: Optional max tokens to generate.
            metadata: Optional request metadata for tracing.

        Returns:
            Parsed JSON response from Bedrock.
        """
        is_openai_oss = self.model_id.startswith("openai.")

        if is_openai_oss:
            # Convert Anthropic-style blocks to OpenAI-style string content
            converted_messages: List[Dict[str, Any]] = []
            if system:
                converted_messages.append({"role": "system", "content": system})
            for msg in messages:
                role = msg.get("role")
                content = msg.get("content")
                text_parts: List[str] = []
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(str(block.get("text", "")))
                elif isinstance(content, str):
                    text_parts.append(content)
                converted_messages.append({"role": role, "content": "\n".join(p for p in text_parts if p)})
            mapped_tools: List[Dict[str, Any]] = []
            body = {"messages": converted_messages}
            if temperature is not None:
                body["temperature"] = temperature
            if max_tokens is not None:
                body["max_tokens"] = max_tokens
            if metadata is not None:
                body["metadata"] = metadata
            if tools:
                # Map to OpenAI tools schema
                mapped_tools: List[Dict[str, Any]] = []
                for t in tools:
                    mapped_tools.append(
                        {
                            "type": "function",
                            "function": {
                                "name": t.get("name"),
                                "description": t.get("description"),
                                "parameters": t.get("input_schema", {}),
                            },
                        }
                    )
                body["tools"] = mapped_tools
                body["parallel_tool_calls"] = True
            if tool_choice is not None:
                body["tool_choice"] = tool_choice
            else:
                # Default to auto selection when tools are provided
                if mapped_tools:
                    body["tool_choice"] = "auto"
        else:
            body: Dict[str, Any] = {"messages": messages}
            if system:
                body["system"] = system
            if tools:
                body["tools"] = tools
            if tool_choice:
                body["tool_choice"] = tool_choice
            if temperature is not None:
                body["temperature"] = temperature
            if max_tokens is not None:
                body["max_tokens"] = max_tokens
            if metadata is not None:
                body["metadata"] = metadata

        attempt = 0
        backoff_seconds = 1.0
        while True:
            try:
                response = self._client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body),
                    accept="application/json",
                    contentType="application/json",
                )
                payload = response.get("body")
                if hasattr(payload, "read"):
                    payload = payload.read()
                if isinstance(payload, (bytes, bytearray)):
                    payload = payload.decode("utf-8")
                return json.loads(payload)
            except Exception as exc:  # Broad except to avoid importing exceptions at module level
                attempt += 1
                if attempt > self._max_retries:
                    raise
                # Exponential backoff with jitter
                time.sleep(backoff_seconds)
                backoff_seconds = min(backoff_seconds * 2.0, 8.0)


def build_tool_config(tools: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Helper to construct Bedrock tool config object."""
    return {"tools": tools}

