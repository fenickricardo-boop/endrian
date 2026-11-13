from __future__ import annotations
from typing import Any, Dict
from .model_schema import ModelProposal

FORBIDDEN_KEYS = {
    "state", "price", "delivery_window", "payment_status", "order_id",
    "matrix_status", "api_key", "credential", "token", "code", "pseudocode",
    "architecture", "stack", "configuration",
}

ALLOWED_DIMENSIONS = {
    "users", "volume", "frequency", "systems", "autonomy", "data_sensitivity",
    "custom_development", "support", "urgency", "functions", "integration_type",
}


def _validate_action_semantics(data: Dict[str, Any]) -> None:
    action = data.get("action")
    extracted = {k: v for k, v in (data.get("extracted") or {}).items() if v is not None}
    if action == "ASK_MATERIAL_QUESTION" and not (data.get("question") or "").strip():
        raise ValueError("ASK_MATERIAL_QUESTION requires question")
    if action == "UPDATE_INTERPRETATION" and not ((data.get("interpreted_need") or "").strip() or (data.get("objective") or "").strip()):
        raise ValueError("UPDATE_INTERPRETATION requires interpreted_need or objective")
    if action == "EXTRACT_DIMENSIONING" and not extracted:
        raise ValueError("EXTRACT_DIMENSIONING requires at least one extracted dimension")
    if action == "FLAG_HUMAN_REVIEW" and not (data.get("human_review_reason") or "").strip():
        raise ValueError("FLAG_HUMAN_REVIEW requires human_review_reason")
    if action in {"ANSWER_FUNCTIONAL_CLARIFICATION", "REFUSE_IMPLEMENTATION_DETAIL"} and not (data.get("functional_answer") or "").strip():
        raise ValueError(f"{action} requires functional_answer")


def _scan_keys(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            low = str(key).strip().lower()
            if low in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden model field: {path}.{key}")
            _scan_keys(item, f"{path}.{key}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            _scan_keys(item, f"{path}[{i}]")


def validate_proposal(proposal: ModelProposal | Dict[str, Any]) -> Dict[str, Any]:
    model = proposal if isinstance(proposal, ModelProposal) else ModelProposal.model_validate(proposal)
    data = model.model_dump()
    _scan_keys(data)
    _validate_action_semantics(data)
    extracted = {k: v for k, v in data["extracted"].items() if k in ALLOWED_DIMENSIONS and v is not None}
    if isinstance(extracted.get("systems"), list):
        extracted["systems"] = [str(x)[:80] for x in extracted["systems"][:8]]
    if isinstance(extracted.get("functions"), list):
        extracted["functions"] = [str(x)[:80] for x in extracted["functions"][:8]]
    data["extracted"] = extracted
    data["missing_material"] = [str(x)[:180] for x in data.get("missing_material", [])[:8]]
    return data
