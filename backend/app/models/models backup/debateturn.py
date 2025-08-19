from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import mapped_column, Mapped

class DebateTurnBase(SQLModel):
    cross_question_text: str
    response_text: str

class DebateTurn(DebateTurnBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    questioning_perspective_id: int = Field(foreign_key="perspective.id")
    critiqued_perspective_id: int = Field(foreign_key="perspective.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    scenario_id: Optional[int] = Field(default=None, foreign_key="scenario.id")

    # Relationships
    scenario: Mapped[Optional["Scenario"]] = Relationship(back_populates="debate_turns")
    questioning_perspective: Mapped[Optional["Perspective"]] = Relationship(
        back_populates="questioning_debate_turns",
        sa_relationship_kwargs={"foreign_keys": "DebateTurn.questioning_perspective_id"}
    )
    critiqued_perspective: Mapped[Optional["Perspective"]] = Relationship(
        back_populates="critiqued_debate_turns",
        sa_relationship_kwargs={"foreign_keys": "DebateTurn.critiqued_perspective_id"}
    )