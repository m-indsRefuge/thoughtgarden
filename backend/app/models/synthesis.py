from __future__ import annotations
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import mapped_column, Mapped

class SynthesisBase(SQLModel):
    synthesis_text: str
    reasoning_steps: Optional[str] = None

class Synthesis(SynthesisBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    scenario_id: Optional[int] = Field(
        default=None,
        foreign_key="scenario.id",
        unique=True
    )

    # Relationships
    scenario: Mapped[Optional["Scenario"]] = Relationship(back_populates="synthesis")