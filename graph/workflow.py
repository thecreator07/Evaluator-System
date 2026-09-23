from langgraph.graph import END, START, StateGraph

from graph.nodes import evaluate_node, generate_node, persist_memory,draft_rules,save_memory,human_review
from graph.routing import route_after_evaluation,increment_attempt
from models.models import EvaluationState
from services.checkpointer import get_checkpointer
from helpers.export_nodes import export_failed_lesson,export_failure_log,export_passed_lesson


def build_workflow(checkpointer=None):
    """Build the lesson evaluation workflow."""

    graph = StateGraph(EvaluationState)
 
    graph.add_node("generate", generate_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("increment_attempt", increment_attempt)
    graph.add_node("export_passed_lesson", export_passed_lesson)
    graph.add_node("export_failed_lesson", export_failed_lesson)
    graph.add_node("draft_rules", draft_rules)
    graph.add_node("human_review", human_review)
    graph.add_node("save_memory", save_memory)
    graph.add_node("persist_memory", persist_memory)
    graph.add_node("export_failure_log", export_failure_log)
 
    graph.add_edge(START, "generate")
    graph.add_edge("generate", "evaluate")
    graph.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "success": "export_passed_lesson",  # Pdf of passed lesson
            "retry": "increment_attempt",
            "failure": "export_failed_lesson",  # PDF of failed lesson
        },
    )
    graph.add_edge("increment_attempt", "generate")
    graph.add_edge("export_passed_lesson", "persist_memory") 
    graph.add_edge("export_failed_lesson", "draft_rules")
    graph.add_edge("draft_rules", "human_review")
    graph.add_edge("human_review", "save_memory")
    graph.add_edge("save_memory", "persist_memory")
    graph.add_edge("persist_memory", "export_failure_log")  # full rejection log
    graph.add_edge("export_failure_log", END)

    return graph.compile(checkpointer=checkpointer or get_checkpointer())