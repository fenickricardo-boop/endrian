from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List
import os

from .model_schema import ModelProposal
from .model_validator import validate_proposal

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


class DeterministicModelAdapter:
    def interpret(self, payload: Dict[str, Any]) -> ModelAdapterResult:
        return ModelAdapterResult(
            proposal=None,
            used_real_model=False,
            valid=True,
            attempts=0,
            fallback_reason="deterministic mode",
        )
