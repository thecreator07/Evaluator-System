from typing import Literal
from pydantic import BaseModel,Field


class Lesson(BaseModel):
    topic: str
    title: str
    introduction: str
    definition: str
    why: str
    workflow: list[str]
    example: list[str]
    key_terms: list[dict[str, str]]
    summary: str

class RubricCriterion(BaseModel):
    id:str
    description:str
    pass_condition:str

class CriterionCheck(BaseModel):
    criterion_id: str
    status: Literal["PASS", "FAIL"]
    reason: str


class EvaluatorResponse(BaseModel):
    checks: list[CriterionCheck]
    regeneration_instructions: list[str]
    overall_status: Literal["PASS", "FAIL"]

class RejectionRecord(BaseModel):
    attempt: int
    failed_criteria: list[str]
    reasons: list[str]
    regeneration_instructions: list[str]


class EvaluationState(BaseModel):
    topic: str
    lesson: Lesson | None =None
    evaluation: EvaluatorResponse | None = None
    rejection_log: list[RejectionRecord] = Field(default_factory=list)
    attempt: int = 1
    max_retries: int = 2
    final_status: Literal["PASS", "FAIL"] | None = None