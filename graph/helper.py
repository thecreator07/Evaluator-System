from collections import defaultdict
from models.memory_models import RuleCandidate 
from services.mongo_store import get_criterion_failure_history
from services.llm import get_llm
from models.models import RejectionRecord



def draft_candidate_rules(
    topic: str,
    rejection_log: list[RejectionRecord],
) -> list[dict]:
    """One draft per criterion that failed in this run.
    occurrences = failures in this run + past runs on the topic.
    rule_type= defaults to "generation", the reviewer may change it.
    """

    reasons_by_criterion: dict[str, list[str]] = defaultdict(list)
    for rejection in rejection_log:
        for criterion, reason in zip(rejection.failed_criteria, rejection.reasons):
            reasons_by_criterion[criterion].append(reason)

    return [
        RuleCandidate(
            rule=_distill_rule(criterion_id, reasons),
            rule_type="generation",
            topic=topic,
            source_criteria=[criterion_id],
            occurrences=len(reasons) + get_criterion_failure_history(topic, criterion_id),
            approved=False,
        ).model_dump()
        for criterion_id, reasons in reasons_by_criterion.items()
    ]


def _distill_rule(criterion_id: str, reasons: list[str]) -> str:
    """Collapse repeated failure reasons into one reusable instruction."""

    reason_lines = "\n".join(f"- {reason}" for reason in reasons)
    prompt = (
        f"A lesson repeatedly failed rubric criterion '{criterion_id}' for these reasons:\n"
        f"{reason_lines}\n\n"
        "Write ONE short generalizable instruction (max 20 words) a lesson "
        "writer should follow on this topic to avoid this failure going forward. "
        "Return only the instruction, no preamble."
    )
    return get_llm().invoke(prompt).content.strip()