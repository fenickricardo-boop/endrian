from dataclasses import replace
from typing import get_args
import pytest

from app.config import settings as base_settings
from app.model_adapter import ModelAdapterResult
from app.model_schema import ModelProposal
from app.model_validator import validate_proposal
from app.service import GuideService, CONSUMED_MODEL_ACTIONS
from app.session_repository import SessionRepository


class StubAdapter:
    def __init__(self, proposal):
        self.proposal = validate_proposal(proposal)
    def interpret(self, payload):
        return ModelAdapterResult(
            proposal=self.proposal,
            used_real_model=True,
            valid=True,
            attempts=1,
        )


def make_service(tmp_path):
    s = replace(base_settings, model_mode="deterministic", db_path=str(tmp_path / "qa.db"), cookie_secure=False)
    return GuideService(s, SessionRepository(s.db_path, ttl_seconds=3600))


def declared_actions():
    return set(get_args(ModelProposal.model_fields["action"].annotation))


def test_every_declared_schema_action_has_real_consumer():
    assert declared_actions() == CONSUMED_MODEL_ACTIONS
    assert "DRAFT_ORIENTATION" not in declared_actions()


def test_flag_human_review_is_consumed_by_deterministic_policy(tmp_path):
    service = make_service(tmp_path)
    service.model_adapter = StubAdapter({
        "action": "FLAG_HUMAN_REVIEW",
        "human_review_reason": "Contradicción material no resoluble automáticamente",
        "extracted": {},
    })
    out = service.chat("MODEL-REVIEW-01", "Necesito organizar correos y dar seguimiento en Gmail")
    assert out["event"] == "HUMAN_REVIEW_REQUIRED"
    assert out["state"] == "REVISIÓN HUMANA REQUERIDA"
    core = service.runtime.core.sessions["MODEL-REVIEW-01"]
    assert core.state == "REVISIÓN HUMANA REQUERIDA"
    assert core.orientation == {}
    assert core.proposal == {}
    assert core.order is None
    assert "SEÑAL VALIDADA DEL MODELO" in core.human_review_reason


def test_noop_does_not_create_human_review(tmp_path):
    service = make_service(tmp_path)
    service.model_adapter = StubAdapter({"action": "NO_OP", "extracted": {}})
    out = service.chat("MODEL-NOOP-01", "Necesito organizar correos y dar seguimiento en Gmail")
    assert out["event"] == "PRELIMINARY_UNDERSTANDING"
    assert out["state"] != "REVISIÓN HUMANA REQUERIDA"


def test_flag_human_review_requires_reason():
    with pytest.raises(ValueError, match="human_review_reason"):
        validate_proposal({"action": "FLAG_HUMAN_REVIEW", "extracted": {}})


def test_removed_decorative_action_is_rejected():
    with pytest.raises(Exception):
        ModelProposal.model_validate({"action": "DRAFT_ORIENTATION", "extracted": {}})
