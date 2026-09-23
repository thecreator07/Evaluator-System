from langfuse.langchain import CallbackHandler

_handler = None


def get_langfuse_handler() -> CallbackHandler:
    """Lazy singleton, same pattern as every other service in this project -
    no network access until a graph is actually invoked."""

    global _handler
    if _handler is None:
        _handler = CallbackHandler()
    return _handler


def traced_config(thread_id: str) -> dict:
    """The {"callbacks": ..., "metadata": ...} fragment every .invoke() call
    needs. Using thread_id as langfuse_session_id groups a lesson's full
    lifecycle - including a pause-and-resume across an interrupt, which is
    two separate .invoke() calls - into one Langfuse session instead of two
    disconnected traces."""

    return {
        "callbacks": [get_langfuse_handler()],
        "metadata": {"langfuse_session_id": thread_id},
    }