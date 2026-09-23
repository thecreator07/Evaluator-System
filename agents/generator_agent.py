from langchain_core.messages import HumanMessage, SystemMessage
from models.models import Lesson
from prompts.generator_system_prompt import GENERATOR_SYSTEM_PROMPT
from services.llm import get_llm


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)

def _build_user_prompt(
    topic: str,
    feedback: list[str],
    failed_criteria: list[str],
    learned_rules: list[str],
) -> str:
    sections = [f"Create a complete beginner-friendly lesson about:\n\n{topic}"]

    if learned_rules:
        sections.append(
            "Standing rules for this topic - apply on every attempt:\n"
            + _bullets(learned_rules)
        )

    if feedback:
        criteria = f" in criteria {', '.join(failed_criteria)}" if failed_criteria else ""
        sections.append(
            "The previous lesson failed evaluation.\n\n"
            f"Fix the following issues{criteria}:\n{_bullets(feedback)}\n\n"
            "You must correct every issue in the new lesson."
        )

    sections.append("Return only the lesson content.")
    return "\n\n".join(sections)


def generate_lesson(
    topic: str,
    feedback: list[str] | None = None,
    failed_criteria: list[str] | None = None,
    learned_rules: list[str] | None = None,
) -> Lesson:
    """Generate a lesson. On retry, `feedback` carries the evaluator's instructions."""

    prompt = _build_user_prompt(
        topic,
        feedback or [],
        failed_criteria or [],
        learned_rules or [],
    )
    llm = get_llm().with_structured_output(Lesson)
    return llm.invoke(
        [SystemMessage(content=GENERATOR_SYSTEM_PROMPT), HumanMessage(content=prompt)]
    )