from models.models import RubricCriterion

RUBRIC:list[RubricCriterion] = [
    RubricCriterion(
        id="accuracy",
        description="The lesson must contain factually correct and grounded information about the requested topic.",
        pass_condition="All explanations are accurate, with no misleading or unsupported claims."
    ),
    RubricCriterion(
        id="beginner_language",
        description="The lesson must be understandable to a learner with no prior knowledge of the topic.",
        pass_condition="The lesson uses simple language and clearly explains concepts for a complete beginner."
    ),
    RubricCriterion(
        id="definition",
        description="The lesson must clearly explain what the requested topic means.",
        pass_condition="The topic is accurately defined in simple and understandable language."
    ),
    RubricCriterion(
        id="why",
        description="The lesson must explain why the topic is useful, relevant, or important.",
        pass_condition="The lesson clearly explains the topic's purpose, importance, or practical value."
    ),
    RubricCriterion(
        id="workflow",
        description="The lesson must explain how the topic works or how its main process is performed, when applicable.",
        pass_condition="The relevant process is explained clearly and logically, or the lesson explains the topic's main mechanism when no workflow applies."
    ),
    RubricCriterion(
        id="example",
        description="The lesson must include at least one relevant, beginner-friendly example.",
        pass_condition="The lesson contains at least one accurate, concrete, and easy-to-understand example or analogy."
    ),
    RubricCriterion(
        id="jargon",
        description="The lesson must explain important technical or unfamiliar terms.",
        pass_condition="Important terms are explained in simple language before or when they are introduced."
    ),
    RubricCriterion(
        id="standalone",
        description="The lesson must be understandable without external context.",
        pass_condition="The lesson provides sufficient context for a beginner to understand the topic without external resources."
    ),
    RubricCriterion(
        id="structure",
        description="The lesson must follow a clear and logical teaching flow.",
        pass_condition="The content progresses logically from basic concepts to explanations and examples."
    ),
]