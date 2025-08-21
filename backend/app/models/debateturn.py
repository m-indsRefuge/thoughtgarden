# file: backend/app/models/debateturn.py
from typing import List, Optional
from sqlmodel import Field, SQLModel, JSON, Column
from app.schemas.schemas import DebateArgument


class DebateTurn(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    turn_number: int
    experiment_id: int
    user_message: str
    debate: List[DebateArgument] = Field(sa_column=Column(JSON))
    internal_monologue: str
    ai_question_to_user: str