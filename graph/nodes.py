from agents.evaluator_agent import evaluate_lesson
from agents.generator_agent import generate_lesson
from models.models import RejectionRecord,EvaluationState
import json

def generate_node(state: EvaluationState) -> dict:
    """Generate or regenerate a lesson."""

    feedback=[]
    attempt_number = state.attempt
    topic = state.topic
    if state.evaluation is not None:
        feedback = state.evaluation.regeneration_instructions
        

    responce = generate_lesson(
        topic=topic,
        feedback=feedback,
        attempt_number=attempt_number,
    )
    lesson=json.loads(responce.content)
    return {
        "lesson":lesson
    }


def evaluate_node(state: EvaluationState) -> dict:
    """Evaluate the current lesson."""

    response = evaluate_lesson(state.lesson)
    evaluation = json.loads(response.content)

    failed_checks = [
        check
        for check in evaluation["checks"]
        if check["status"] == "FAIL"
    ]

    rejection_log = list(state.rejection_log)

    if failed_checks:
        instructions = evaluation["regeneration_instructions"]

        if isinstance(instructions, str):
            instructions = [instructions]

        rejection = RejectionRecord(
            attempt=state.attempt,
            failed_criteria=[
                check["criterion_id"] for check in failed_checks
            ],
            reasons=[
                check["reason"] for check in failed_checks
            ],
            regeneration_instructions=instructions,
        )

        rejection_log.append(rejection)

    return {
        "evaluation":evaluation,
        "rejection_log":rejection_log,
        "final_status":"FAIL" if failed_checks else "PASS"
    }

    # return updated_state