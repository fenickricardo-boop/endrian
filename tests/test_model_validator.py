import pytest
from app.model_schema import ModelProposal
from app.model_validator import validate_proposal


def test_valid_model_proposal():
    p = ModelProposal(
        action="EXTRACT_DIMENSIONING",
        interpreted_need="Organizar correos y seguimiento",
        extracted={"systems":"Gmail","functions":["organizar","seguimiento"]},
        confidence=0.88,
    )
    out = validate_proposal(p)
    assert out["action"] == "EXTRACT_DIMENSIONING"
    assert out["extracted"]["systems"] == "Gmail"


def test_extra_authority_field_rejected():
    with pytest.raises(Exception):
        ModelProposal.model_validate({
            "action":"NO_OP",
            "extracted":{},
            "state":"PAGO CONFIRMADO"
        })
