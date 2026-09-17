import json
from agents.generator_agent import generate_lesson
from agents.evaluator_agent import evaluate_lesson
from graph.workflow import build_workflow 
from models.models import EvaluationState

def main() -> None:

    
    data_flow=build_workflow()

    while True:
        input_data=input("> ")
        if input_data.lower() in {"/bye","bye","/exit","exit"}:
            break

        initial_state=EvaluationState(topic=input_data)
        result = data_flow.invoke(initial_state)
        print(result)


if __name__ == "__main__":
    main()