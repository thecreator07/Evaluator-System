"""Terminal handling for the human-review interrupt."""

from langgraph.types import Command

RULE_TYPES = {"generation", "evaluation"}


def _prompt_choice(prompt: str, choices: set[str]) -> str:
    while True:
        answer = input(prompt).strip().lower()
        if answer in choices:
            return answer
        print(f"Please enter one of: {', '.join(sorted(choices))}")


def _prompt_rule_type(current: str) -> str:
    while True:
        answer = input(f"Rule type (generation/evaluation) [{current}]: ").strip().lower()
        if not answer:
            return current
        if answer in RULE_TYPES:
            return answer
        print(f"Rule type must be one of: {', '.join(sorted(RULE_TYPES))}")


def _review_candidate(candidate: dict) -> dict | None:
    """Return the approved (possibly edited) candidate, or None if skipped."""

    print(
        f"\nCandidate rule (criteria: {candidate['source_criteria']}, "
        f"seen {candidate['occurrences']}x):"
    )
    print(f"  [{candidate['rule_type']}] {candidate['rule']}")

    choice = _prompt_choice("Approve as-is / edit / skip? [a/e/s]: ", {"a", "e", "s"})
    if choice == "s":
        return None

    if choice == "e":
        edited_rule = input(f"New rule text [{candidate['rule']}]: ").strip()
        candidate = {
            **candidate,
            "rule": edited_rule or candidate["rule"],
            "rule_type": _prompt_rule_type(candidate["rule_type"]),
        }

    return {**candidate, "approved": True}


def ask_human_for_rules(payload: dict) -> dict:
    """Show the interrupt payload; return the decision graph expects on resume."""

    print(f"\nLesson on '{payload['topic']}' failed after all retries.")
    print("Rejection history:")
    for rejection in payload["rejection_log"]:
        print(f"  attempt {rejection['attempt']}: {rejection['failed_criteria']}")

    reviewed = (_review_candidate(c) for c in payload["candidate_rules"])
    return {"approved_rules": [c for c in reviewed if c is not None]}
