"""Persistence models for ThoughtGarden V2."""

from sqlmodel import SQLModel

from app.models.inquiry import Inquiry

__all__ = ["Inquiry", "SQLModel"]
