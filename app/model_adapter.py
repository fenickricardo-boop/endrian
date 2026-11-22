from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List
import os

from .model_schema import ModelProposal
from .model_validator import validate_proposal


def _strip_additional_properties(node: Any) -> None:
    # The Gemini Developer API (as opposed to Vertex AI) rejects any
    # "additionalProperties"/"additional_properties" key in a JSON schema —
    # Pydantic's extra="forbid" config adds it at every object level, so
    # ModelProposal's raw model_json_schema() can't be sent to Gemini as-is.
    if isinstance(node, dict):
        node.pop("additionalProperties", None)
        node.pop("additional_properties", None)
        for value in node.values():
            _strip_additional_properties(value)
    elif isinstance(node, list):
        for item in node:
            _strip_additional_properties(item)


def _gemini_response_schema() -> Dict[str, Any]:
    schema = ModelProposal.model_json_schema()
    _strip_additional_properties(schema)
    return schema

SYSTEM_INSTRUCTIONS = """You are the language interpretation adapter for ENDRIAN Agente Guía QA.
Your output is a structured proposal only. You do not control workflow state, pricing, delivery windows,
payments, orders, commercial classification, or production matrices.
Understand before asking. Ask only when an answer can materially change understanding, scope,
classification, price, timing, risk, or matrix completeness.
Stay at functional/commercial level. Never provide implementation instructions, prompts, code,
pseudocode, architecture, stack, configuration, or a step-by-step build procedure.
Never invent price, timing, viability, capability, or commercial rules.
When the case requires sensitive data, high autonomy, unknown integration, custom development,
contradictory instructions, or other material risk, propose FLAG_HUMAN_REVIEW with a concise material reason.
Use exactly one action matching the intended effect. Do not populate authority-like fields.
The user is in a QA environment and must not provide real personal or sensitive data.
"""


@dataclass
class ModelAdapterResult:
    proposal: Dict[str, Any] | None
    used_real_model: bool
    valid: bool
    attempts: int
    fallback_reason: str | None = None


class OpenAIModelAdapter:
    def __init__(self, model: str, max_output_tokens: int = 700):
        self.model = model
        self.max_output_tokens = max_output_tokens

    def _client(self):
        from openai import OpenAI
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not configured")
        return OpenAI()

    def interpret(self, payload: Dict[str, Any]) -> ModelAdapterResult:
        client = self._client()
        compact_history: List[Dict[str, str]] = []
        for item in payload.get("conversation", [])[-12:]:
            role = item.get("role")
            text = str(item.get("text", ""))[:1200]
            if role in {"user", "assistant"} and text:
                compact_history.append({"role": role, "content": text})
        input_items: List[Dict[str, str]] = list(compact_history)
        latest = str(payload.get("latest_user_message", ""))[:1200]
        if latest:
            input_items.append({"role": "user", "content": latest})
        if not input_items:
            input_items = [{"role": "user", "content": "Continuar conversación QA."}]
        context = {
            "state": payload.get("state"),
            "known": payload.get("known", {}),
            "task": "interpret_next_user_message",
        }
        instructions = SYSTEM_INSTRUCTIONS + "\nCurrent QA context (non-authoritative): " + repr(context)
        last_error = None
        for attempt in (1, 2):
            try:
                response = client.responses.parse(
                    model=self.model,
                    input=input_items,
                    instructions=instructions,
                    text_format=ModelProposal,
                    reasoning={"effort": "low"},
                    max_output_tokens=self.max_output_tokens,
                    store=False,
                )
                parsed = response.output_parsed
                if parsed is None:
                    raise ValueError("structured output missing")
                return ModelAdapterResult(
                    proposal=validate_proposal(parsed),
                    used_real_model=True,
                    valid=True,
                    attempts=attempt,
                )
            except Exception as exc:  # one retry, then deterministic fallback
                last_error = f"{type(exc).__name__}: {exc}"
        return ModelAdapterResult(
            proposal=None,
            used_real_model=True,
            valid=False,
            attempts=2,
            fallback_reason=last_error or "invalid structured output",
        )


class GeminiModelAdapter:
    """Free-tier alternative to OpenAIModelAdapter: same interpret() contract,
    backed by Google's Gemini API (google-genai SDK) instead of OpenAI's
    Responses API. Structured output still goes through ModelProposal /
    validate_proposal, so the rest of the app (service.py, model_validator.py)
    is unaware of which provider produced the proposal."""

    def __init__(self, model: str, max_output_tokens: int = 700):
        self.model = model
        self.max_output_tokens = max_output_tokens

    def _client(self):
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        return genai.Client(api_key=api_key)

    def interpret(self, payload: Dict[str, Any]) -> ModelAdapterResult:
        from google.genai import types
        client = self._client()
        contents: List[Dict[str, Any]] = []
        for item in payload.get("conversation", [])[-12:]:
            role = item.get("role")
            text = str(item.get("text", ""))[:1200]
            if role == "user" and text:
                contents.append({"role": "user", "parts": [{"text": text}]})
            elif role == "assistant" and text:
                contents.append({"role": "model", "parts": [{"text": text}]})
        latest = str(payload.get("latest_user_message", ""))[:1200]
        if latest:
            contents.append({"role": "user", "parts": [{"text": latest}]})
        if not contents:
            contents = [{"role": "user", "parts": [{"text": "Continuar conversación QA."}]}]
        context = {
            "state": payload.get("state"),
            "known": payload.get("known", {}),
            "task": "interpret_next_user_message",
        }
        instructions = SYSTEM_INSTRUCTIONS + "\nCurrent QA context (non-authoritative): " + repr(context)
        config_kwargs = dict(
            system_instruction=instructions,
            response_mime_type="application/json",
            response_schema=_gemini_response_schema(),
            max_output_tokens=self.max_output_tokens,
            temperature=0.2,
        )
        # "-lite" models don't support thinking at all and reject this field
        # outright (400 INVALID_ARGUMENT); non-lite models bill "thinking"
        # tokens against the same output cap as the JSON answer, so it must
        # be explicitly disabled there to avoid truncating mid-response.
        if "lite" not in self.model:
            config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
        config = types.GenerateContentConfig(**config_kwargs)
        last_error = None
        for attempt in (1, 2):
            try:
                response = client.models.generate_content(model=self.model, contents=contents, config=config)
                parsed = response.parsed
                if parsed is None:
                    raise ValueError("structured output missing")
                return ModelAdapterResult(
                    proposal=validate_proposal(parsed),
                    used_real_model=True,
                    valid=True,
                    attempts=attempt,
                )
            except Exception as exc:  # one retry, then deterministic fallback
                last_error = f"{type(exc).__name__}: {exc}"
        return ModelAdapterResult(
            proposal=None,
            used_real_model=True,
            valid=False,
            attempts=2,
            fallback_reason=last_error or "invalid structured output",
        )


class DeterministicModelAdapter:
    def interpret(self, payload: Dict[str, Any]) -> ModelAdapterResult:
        return ModelAdapterResult(
            proposal=None,
            used_real_model=False,
            valid=True,
            attempts=0,
            fallback_reason="deterministic mode",
        )
