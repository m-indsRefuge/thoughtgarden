# file: app/models/base.py
from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class BaseModel(SQLModel):
    """Base model with common fields for all tables"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True,
        description="Timestamp when record was created"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        index=True,
        description="Timestamp when record was last updated",
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )

    class Config:
        arbitrary_types_allowed = True