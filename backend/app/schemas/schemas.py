# file: app/schemas/schemas.py
from sqlmodel import SQLModel
from typing import List, Optional

# --- Individual Components of the Simulation ---

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

# --- The Main Data Structure for the JSON blob ---

class ExperimentData(SQLModel):
    description: str
    perspectives: List[Perspective] = []
    debate_turns: List[DebateTurn] = []
    synthesis: Optional[Synthesis] = None

# --- API Input Schema ---

class ExperimentCreate(SQLModel):
    title: str
    description: str