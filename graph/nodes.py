from langgraph.types import interrupt
from agents.evaluator_agent import evaluate_lesson
from agents.generator_agent import generate_lesson
from models.memory_models import RuleCandidate, RuleRecord
from models.models import EvaluationState, RejectionRecord
from services.mongo_store import persist_run
from services.vector_store import get_evaluation_rules, get_generation_rules, upsert_rule
from graph.helper import draft_candidate_rules

def generate_node(state: EvaluationState) -> dict:
    """Generate or regenerate a lesson."""

    feedback = state.evaluation.regeneration_instructions if state.evaluation else []
    lesson = generate_lesson(
        topic=state.topic,
        feedback=feedback,
        failed_criteria=_latest_failed_criteria(state),
        learned_rules=get_generation_rules(state.topic),
    )
    return {"lesson": lesson}


def _latest_failed_criteria(state: EvaluationState) -> list[str]:
    """Criteria behind the feedback we are about to send: the latest rejection."""
    return state.rejection_log[-1].failed_criteria if state.rejection_log else []


def evaluate_node(state: EvaluationState) -> dict:
    """Evaluate the current lesson and log a rejection if any check fails."""

    evaluation = evaluate_lesson(
        state.lesson,
        extra_rules=get_evaluation_rules(state.topic),
    )
    failed_checks = [check for check in evaluation.checks if check.status == "FAIL"]
    status = "FAIL" if failed_checks else "PASS"

    rejection_log = list(state.rejection_log)
    if failed_checks:
        rejection_log.append(
            RejectionRecord(
                attempt=state.attempt,
                failed_criteria=[check.criterion_id for check in failed_checks],
                reasons=[check.reason for check in failed_checks],
                regeneration_instructions=evaluation.regeneration_instructions
            )
        )

    return {
        "evaluation": evaluation.model_copy(update={"overall_status": status}),
        "rejection_log": rejection_log,
        "final_status": status,
    }


def persist_memory(state: EvaluationState) -> dict:
    """Store the finished run (pass or retries exhausted) in episodic memory."""

    persist_run(state)
    return {}


def draft_rules(state: EvaluationState) -> dict:
    """Runs exactly once, before human_review_node. The LLM calls that distill
    candidate rules belong here: this node's output is checkpointed, so unlike
    human_review_node it is NOT recomputed when the graph resumes."""

    return {"candidate_rules": draft_candidate_rules(state.topic, state.rejection_log)}


def human_review(state: EvaluationState) -> dict:
    """Only calls interrupt(). LangGraph re-runs this function from the top on
    resume, so it must stay free of side effects (LLM calls, writes).

    Resume with Command(resume={"approved_rules": [<RuleCandidate dict>, ...]})."""

    decision = interrupt(
        {
            "topic": state.topic,
            "lesson": state.lesson.model_dump(),
            "rejection_log": [r.model_dump() for r in state.rejection_log],
            "candidate_rules": state.candidate_rules,
        }
    )
    return {"human_decision": decision}


def save_memory(state: EvaluationState) -> dict:
    """Write only the rules the reviewer approved. `approved` is stripped: it
    only matters during the review round-trip, not in the stored record."""

    approved_rules = (state.human_decision or {}).get("approved_rules", [])
    for raw in approved_rules:
        candidate = RuleCandidate.model_validate(raw)
        if candidate.approved:
            upsert_rule(
                RuleRecord.model_validate(candidate.model_dump(exclude={"approved"}))
            )
    return {}
