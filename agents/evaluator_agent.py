from langchain_core.messages import HumanMessage, SystemMessage
from models.models import EvaluatorResponse, Lesson
from prompts.evaluator_system_prompt import EVALUATOR_SYSTEM_PROMPT
from services.llm import get_llm


def evaluate_lesson(
    lesson: Lesson,
    extra_rules: list[str] | None = None,
) -> EvaluatorResponse:
    """Evaluate a lesson against the full rubric plus any human-curated rules."""

    request = f"Evaluate the following lesson.\n\n{lesson.model_dump_json(indent=2)}"
    if extra_rules:
        rules = "\n".join(f"- {rule}" for rule in extra_rules)
        request += (
            "\n\nAlso apply these additional, human-curated rules for this topic:\n"
            f"{rules}"
        )

    llm = get_llm().with_structured_output(EvaluatorResponse)
    return llm.invoke(
        [SystemMessage(content=EVALUATOR_SYSTEM_PROMPT), HumanMessage(content=request)]
    )