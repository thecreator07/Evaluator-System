from typing import Literal
from models.models import EvaluationState,EvaluatorResponse


def route_after_evaluation(state: EvaluationState):
    evaluation = EvaluatorResponse.model_validate(state.evaluation)

    has_failures = any(
        check.status == "FAIL"
        for check in evaluation.checks
    )

    if not has_failures:
        return "success"

    if state.attempt <= state.max_retries:
        return "retry"

    return "failure"


def increment_attempt(state: EvaluationState) -> dict:
    return {
        "attempt":state.attempt+1
    }