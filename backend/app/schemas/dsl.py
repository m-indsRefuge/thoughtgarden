# file: backend/app/schemas/dsl.py
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from uuid import uuid4

# --- Action & Strategy Schemas for the new Reasoning DSL ---

# A simple type for actions within a strategy
ActionType = Literal[
    "tool_use",
    "generate_text",
    "query_db",
    "summarize",
    "reflect",
    "critique",
]

# New models for structured strategy components
class Constraint(BaseModel):
    """
    A structured constraint for a strategy.
    """
    type: str
    value: Any
    unit: Optional[str] = None
    description: Optional[str] = None

class Mutator(BaseModel):
    """
    An algorithmic mutator to apply to a strategy.
    """
    type: str
    description: str

class ExpectedOutput(BaseModel):
    """
    An expected output from the execution of a strategy.
    """
    metric: str
    description: str

class Action(BaseModel):
    """
    A single step within a larger reasoning strategy.
    """
    type: ActionType
    step_description: str = Field(..., description="A description of what the action does.")
    input_data: Optional[Dict[str, Any]] = None

class Strategy(BaseModel):
    """
    The canonical representation of a reasoning plan, in a structured format.
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="A unique identifier for the strategy.")
    goal: str = Field(..., description="The high-level objective of the strategy.")
    priority: float = Field(..., ge=0, le=1, description="The priority of this strategy, from 0.0 (low) to 1.0 (high).")
    constraints: List[Constraint] = Field(default_factory=list, description="List of structured constraints.")
    lenses: List[str] = Field(default_factory=list, description="List of perspectives or filters to apply.")
    mutators: List[Mutator] = Field(default_factory=list, description="List of algorithmic mutators to use.")
    actions: List[Action] = Field(..., description="A sequence of actions to execute the strategy.")

    # A simple example for documentation/schema generation
    class Config:
        schema_extra = {
            "example": {
                "id": str(uuid4()),
                "goal": "Generate a compelling counterpoint to the user's argument.",
                "priority": 0.9,
                "constraints": [{"type": "budget", "value": 100, "unit": "$"}],
                "lenses": ["contrarian", "logical-fallacy-finder"],
                "mutators": [{"type": "analogy_leap", "description": "Analogical leap to a beehive."}],
                "actions": [
                    {"type": "reflect", "step_description": "Review user's last input for core logical premise."},
                    {"type": "critique", "step_description": "Identify the weakest point in the premise."},
                    {"type": "generate_text", "step_description": "Formulate a counterpoint based on the identified weakness."}
                ]
            }
        }