from langgraph.graph import END, START, StateGraph

from graph.nodes import evaluate_node, generate_node
from graph.routing import route_after_evaluation,increment_attempt
from models.models import EvaluationState


def build_workflow():
    """Build the lesson evaluation workflow."""

    graph = StateGraph(EvaluationState)

    graph.add_node("generate", generate_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("increment_attempt", increment_attempt)

    graph.add_edge(START, "generate")
    graph.add_edge("generate", "evaluate")

    graph.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "success": END,
            "retry": "increment_attempt",
            "failure": END,
        },
    )

    graph.add_edge("increment_attempt","generate")

    return graph.compile()