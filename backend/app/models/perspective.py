from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import mapped_column, Mapped

class PerspectiveBase(SQLModel):
    viewpoint_name: str
    viewpoint_text: str

class Perspective(PerspectiveBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    scenario_id: Optional[int] = Field(default=None, foreign_key="scenario.id")

    # Relationships
    scenario: Mapped[Optional["Scenario"]] = Relationship(back_populates="perspectives")
    questioning_debate_turns: Mapped[List["DebateTurn"]] = Relationship(
        back_populates="questioning_perspective",
        sa_relationship_kwargs={"foreign_keys": "DebateTurn.questioning_perspective_id"}
    )
    critiqued_debate_turns: Mapped[List["DebateTurn"]] = Relationship(
        back_populates="critiqued_perspective",
        sa_relationship_kwargs={"foreign_keys": "DebateTurn.critiqued_perspective_id"}
    )