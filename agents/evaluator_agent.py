import json

from langchain_core.messages import HumanMessage, SystemMessage

from prompts.evaluator_system_prompt import EVALUATOR_SYSTEM_PROMPT
from models.models import Lesson,EvaluatorResponse
from services.llm import get_llm




def evaluate_lesson(data:Lesson) -> EvaluatorResponse:
    """Evaluate a lesson against the complete rubric."""

    llm = get_llm()


    evaluation_request = f"""
Evaluate the following lesson.
{data}
"""

    messages = [
        SystemMessage(content=EVALUATOR_SYSTEM_PROMPT),
        HumanMessage(content=evaluation_request),
    ]


    response = llm.invoke(messages)
    return response