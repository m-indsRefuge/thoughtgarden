"""Provider-neutral ports for future model and corpus integrations."""

from __future__ import annotations

from typing import Protocol, Sequence

from pydantic import BaseModel, Field

from app.praxis.contracts import DeliberationPhase, MindId, Submission


class CorpusPassage(BaseModel):
    passage_id: str = Field(min_length=1)
    work: str = Field(min_length=1)
    locator: str = Field(min_length=1)
    text: str = Field(min_length=1)
    translator: str | None = None
    edition: str | None = None


class MindContext(BaseModel):
    mind: MindId
    question: str = Field(min_length=1)
    phase: DeliberationPhase
    prior_submissions: list[dict] = Field(default_factory=list)
    passages: list[CorpusPassage] = Field(default_factory=list)


class CorpusRetriever(Protocol):
    async def retrieve(
        self,
        *,
        mind: MindId,
        query: str,
        limit: int = 6,
    ) -> Sequence[CorpusPassage]: ...


class MindAdapter(Protocol):
    async def respond(self, context: MindContext) -> Submission: ...
