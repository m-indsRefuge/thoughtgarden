from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import mapped_column, Mapped

class ScenarioBase(SQLModel):
    title: str
    description: str

class Scenario(ScenarioBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    
    # Relationships
    perspectives: Mapped[List["Perspective"]] = Relationship(
        back_populates="scenario",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    debate_turns: Mapped[List["DebateTurn"]] = Relationship(
        back_populates="scenario",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    synthesis: Mapped[Optional["Synthesis"]] = Relationship(
        back_populates="scenario",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"}
    )