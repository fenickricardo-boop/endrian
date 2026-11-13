from __future__ import annotations
from typing import Optional, Union, List
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Literal


class ExtractedDimensions(BaseModel):
    model_config = ConfigDict(extra="forbid")
    users: Optional[int] = Field(default=None, ge=1, le=1000000)
    volume: Optional[str] = Field(default=None, max_length=120)
    frequency: Optional[str] = Field(default=None, max_length=80)
    systems: Optional[Union[str, List[str]]] = None
    autonomy: Optional[str] = Field(default=None, max_length=80)
    data_sensitivity: Optional[str] = Field(default=None, max_length=80)
    custom_development: Optional[bool] = None
    support: Optional[str] = Field(default=None, max_length=120)
    urgency: Optional[str] = Field(default=None, max_length=120)
    functions: Optional[List[str]] = None
    integration_type: Optional[str] = Field(default=None, max_length=80)


class ModelProposal(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal[
        "ASK_MATERIAL_QUESTION",
        "UPDATE_INTERPRETATION",
        "EXTRACT_DIMENSIONING",
        "FLAG_HUMAN_REVIEW",
        "ANSWER_FUNCTIONAL_CLARIFICATION",
        "REFUSE_IMPLEMENTATION_DETAIL",
        "NO_OP",
    ]
    interpreted_need: Optional[str] = Field(default=None, max_length=700)
    objective: Optional[str] = Field(default=None, max_length=500)
    extracted: ExtractedDimensions = Field(default_factory=ExtractedDimensions)
    missing_material: List[str] = Field(default_factory=list, max_length=10)
    contradiction: Optional[str] = Field(default=None, max_length=400)
    human_review_reason: Optional[str] = Field(default=None, max_length=400)
    question: Optional[str] = Field(default=None, max_length=400)
    functional_answer: Optional[str] = Field(default=None, max_length=900)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
