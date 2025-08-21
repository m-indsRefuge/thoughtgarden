# file: backend/app/models/synthesis.py
from typing import Optional, List
from sqlmodel import Field, SQLModel, JSON, Column
from app.schemas.schemas import Synthesis as SynthesisSchema


class Synthesis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    turn_id: int
    summary: str
    key_points: List[str] = Field(sa_column=Column(JSON))
    new_questions: List[str] = Field(sa_column=Column(JSON))