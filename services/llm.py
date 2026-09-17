from langchain_ollama import ChatOllama
from config.settings import settings


def get_llm() -> ChatOllama:
    """Create the local Ollama chat model."""
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=0.2,
        keep_alive="5m",
        num_ctx=8192,
        num_gpu=99,
        num_predict=1500,
    )