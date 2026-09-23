from typing import Literal
from pydantic import BaseModel

class RuleRecord(BaseModel):
    """ """
    rule: str
    rule_type: Literal["generation", "evaluation"]
    topic: str
    source_criteria: list[str]
    occurrences: int

class RuleCandidate(RuleRecord):
    """What human_review_node sends via interrupt() and expects back on
    resume - same fields as RuleRecord, plus the reviewer's decision."""
 
    approved: bool = False