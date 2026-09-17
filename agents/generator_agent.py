from langchain_core.messages import HumanMessage, SystemMessage
from models.models import Lesson
from services.llm import get_llm
from prompts.generator_system_prompt import GENERATOR_SYSTEM_PROMPT

def generate_lesson(
    topic: str = "Introduction to RAG",
    feedback: list[str] | None = None,
    attempt_number: int = 1,
) -> Lesson:
    """
    Generate a lesson.

    On retry, feedback contains instructions from the evaluator.
    """

    llm = get_llm()

    feedback_text = ""

    if feedback:
        feedback_text = f"""
The previous lesson failed evaluation.

Fix the following issues:
{chr(10).join(f"- {item}" for item in feedback)}

You must correct every issue in the new lesson.
"""

    user_prompt = f"""
Create a complete beginner-friendly lesson about:

{topic}

{feedback_text}
also the attemp is {attempt_number}.it should less than and equal to 2
Return only the lesson content.
"""

    messages = [
        SystemMessage(content=GENERATOR_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    return response
    # return Lesson(
    #     topic=topic,
    #     title="Introduction to Retrieval-Augmented Generation",
    #     content=response.content,
    #     attempt_number=attempt_number,
    # )