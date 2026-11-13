import os
from types import SimpleNamespace
from app.model_adapter import OpenAIModelAdapter
from app.model_schema import ModelProposal


class FakeResponses:
    def __init__(self):
        self.kwargs = None
    def parse(self, **kwargs):
        self.kwargs = kwargs
        parsed = ModelProposal(action="NO_OP", extracted={})
        return SimpleNamespace(output_parsed=parsed)


class FakeClient:
    def __init__(self):
        self.responses = FakeResponses()


def test_real_adapter_uses_store_false_and_low_reasoning(monkeypatch):
    adapter = OpenAIModelAdapter("gpt-5.6-terra", 700)
    fake = FakeClient()
    monkeypatch.setattr(adapter, "_client", lambda: fake)
    result = adapter.interpret({"conversation":[],"latest_user_message":"Necesito ordenar correos","state":"CONVERSACIÓN INICIAL","known":{}})
    assert result.valid is True
    assert fake.responses.kwargs["store"] is False
    assert fake.responses.kwargs["reasoning"] == {"effort":"low"}
    assert fake.responses.kwargs["max_output_tokens"] == 700
