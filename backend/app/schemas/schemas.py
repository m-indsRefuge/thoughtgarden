# file: app/schemas/schemas.py

from sqlmodel import SQLModel
from typing import List, Optional

# --- Existing schemas for the one-shot simulation ---

class Perspective(SQLModel):
    id: int
    viewpoint_name: str
    viewpoint_text: str

class DebateTurn(SQLModel):
    questioning_perspective_id: int
    critiqued_perspective_id: int
    questioner_name: str
    critiqued_name: str
    cross_question_text: str
    response_text: str

class Synthesis(SQLModel):
    synthesis_text: str
    reasoning_steps: Optional[str] = None

class ExperimentData(SQLModel):
    description: str
    perspectives: List[Perspective] = []
    debate_turns: List[DebateTurn] = []
    synthesis: Optional[Synthesis] = None

# --- API Input Schema for Simulation ---

class ExperimentCreate(SQLModel):
    title: str
    description: str

# --- NEW SCHEMAS for the interactive, turn-by-turn conversation flow ---

class DebateArgument(SQLModel):
    """A single persona's argument during the internal debate."""
    persona: str
    argument: str
    score: int

class UserInput(SQLModel):
    """The schema for the user's input in the /advance endpoint."""
    message: str

class Turn(SQLModel):
    """Represents a single, complete turn in the conversation."""
    turn_number: int
    user_message: str
    debate: List[DebateArgument] = []
    internal_monologue: str
    ai_question_to_user: str

class ConversationData(SQLModel):
    """The main data structure for storing the entire conversation in the JSON blob."""
    description: str
    history: List[Turn] = []

# Add to the end of app/schemas/schemas.py

# --- NEW SCHEMAS for the Journeyman (pre-scripted) flow ---

class JourneymanState(SQLModel):
    """The data structure for storing the state of a pre-scripted journey."""
    journey_id: str
    locked_in_persona: str | None = None
    current_step: int = 0

class JourneymanTurn(SQLModel):
    """The response model for a single turn in a Journeyman journey."""
    narrative: str
    is_complete: bool = False    