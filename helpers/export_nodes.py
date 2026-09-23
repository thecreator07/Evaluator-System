"""Graph nodes that save PDFs.

They are separate nodes, never part of human_review_node: that node is re-run
from the top when the graph resumes after the interrupt, and a file write must
not repeat.
"""

import logging
import re
from collections.abc import Callable
from pathlib import Path

from langchain_core.runnables import RunnableConfig

from config.settings import settings
from models.models import EvaluationState
from helpers.export_pdf import write_lesson_pdf, write_rejection_log_pdf

logger = logging.getLogger(__name__)


def export_passed_lesson(state: EvaluationState, config: RunnableConfig) -> dict:
    """Right after the lesson passes evaluation."""

    return _export(
        "the lesson PDF",
        lambda: write_lesson_pdf(state.lesson, _run_dir(config) / "lesson.pdf"),
    )


def export_failed_lesson(state: EvaluationState, config: RunnableConfig) -> dict:
    """After retries are exhausted and before the human review."""

    banner = f"NOT SHIPPED: this lesson failed evaluation after {state.attempt} attempts."
    return _export(
        "the failed lesson PDF",
        lambda: write_lesson_pdf(state.lesson, _run_dir(config) / "lesson_failed.pdf", banner=banner),
    )


def export_failure_log(state: EvaluationState, config: RunnableConfig) -> dict:
    """After persist_memory: every rejection of the run, as the assessment output."""

    return _export(
        "the rejection log PDF",
        lambda: write_rejection_log_pdf(state, _run_dir(config) / "rejection_log.pdf"),
    )


def _export(description: str, write: Callable[[], Path]) -> dict:
    """Run one export without ever failing the graph.

    A PDF is a by-product of the run. If saving it raised, a lesson that
    already passed would never reach persist_memory and the run would be lost,
    so a failure is logged with its traceback and the run carries on.
    """
    try:
        print(f"Saved: {write()}")
    except Exception:
        logger.exception("Could not save %s", description)
    return {}


def _run_dir(config: RunnableConfig) -> Path:
    """output/<user>/<run>/. The thread id is 'user:uuid', so users never share a folder."""

    user, _, run = config["configurable"]["thread_id"].partition(":")
    return Path(settings.output_dir) / _folder_name(user) / _folder_name(run or "run")


def _folder_name(text: str) -> str:
    """Keep user-typed text from escaping the output folder (no slashes, no '..')."""
    return re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("-.") or "unknown"