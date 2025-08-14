# file: app/models/experiment.py
from __future__ import annotations
from typing import Dict, Any
from datetime import datetime

from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import JSON

class Experiment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # The entire simulation (description, perspectives, debates, synthesis) lives here.
    data: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))