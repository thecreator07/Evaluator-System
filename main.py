import uuid
from pprint import pprint

from dotenv import load_dotenv
from langfuse import get_client, propagate_attributes
from langfuse.langchain import CallbackHandler
from langgraph.types import Command

from config.settings import settings
from graph.workflow import build_workflow
from services.interrupt_handler import ask_human_for_rules
from services.checkpointer import get_checkpointer

load_dotenv()  # the Langfuse SDK reads os.environ, not pydantic settings

RUN_NAME = "lesson-evaluation-workflow"


def _read_required(label: str) -> str:
    value = input(f"{label} > ").strip()
    if not value:
        raise SystemExit(f"{label} cannot be empty.")
    return value


def _make_thread_id(user_id: str) -> str:
    """One thread per run, namespaced by user."""
    return f"{user_id}:{uuid.uuid4()}"


def _delete_finished_thread(thread_id: str) -> None:
    if settings.delete_finished_threads:
        get_checkpointer().delete_thread(thread_id)


def main() -> None:
    user_id = _read_required("user")
    topic = _read_required("topic")

    langfuse = get_client()
    workflow = build_workflow()
    thread_id = _make_thread_id(user_id)
    print(f"thread: {thread_id}")

    config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": [CallbackHandler()],
        "run_name": RUN_NAME,
    }

    with langfuse.start_as_current_observation(
        as_type="span",
        name=RUN_NAME,
        trace_context={"trace_id": langfuse.create_trace_id()},
    ) as root_span:
        root_span.update(input={"user_id": user_id, "topic": topic})

        with propagate_attributes(
            trace_name=RUN_NAME,
            user_id=user_id,
            session_id=thread_id,
            tags=["langgraph", "ollama", settings.ollama_model],
            metadata={"thread_id": thread_id},
        ):
            result = workflow.invoke({"topic": topic}, config=config)
            while "__interrupt__" in result:
                payload = result["__interrupt__"][0].value
                decision = ask_human_for_rules(payload)
                result = workflow.invoke(Command(resume=decision), config=config)
                return result
            
            root_span.update(output=result)

    # Reached only on success: a crashed run keeps its checkpoints for resuming.
    _delete_finished_thread(thread_id)

    pprint(result, width=120, sort_dicts=False)
    langfuse.flush()


if __name__ == "__main__":
    main()