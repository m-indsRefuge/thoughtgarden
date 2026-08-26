"""Typed constitutional contracts for the ThoughtGarden V2 Praxis engine."""

from __future__ import annotations

from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, model_validator


class MindId(str, Enum):
    PLATONIC = "platonic"
    NIETZSCHEAN = "nietzschean"
    FAUSTIAN = "faustian"


GOVERNED_MINDS: tuple[MindId, ...] = tuple(MindId)


class DeliberationPhase(str, Enum):
    INDEPENDENT_THESIS = "independent_thesis"
    CHALLENGE = "challenge"
    REVISION = "revision"
    CONSENSUS_PROPOSAL = "consensus_proposal"
    RATIFICATION = "ratification"


BOUNDED_PHASES: tuple[DeliberationPhase, ...] = tuple(DeliberationPhase)


class RevisionDisposition(str, Enum):
    MAINTAINED = "maintained"
    REVISED = "revised"
    PARTIALLY_CONCEDED = "partially_conceded"
    WITHDRAWN = "withdrawn"


class RatificationDecision(str, Enum):
    RATIFY = "ratify"
    RATIFY_WITH_RESERVATION = "ratify_with_reservation"
    REJECT = "reject"


class SourceReference(BaseModel):
    passage_id: str = Field(min_length=1)
    work: str = Field(min_length=1)
    locator: str = Field(min_length=1)
    quote: str | None = None


class SupportedClaim(BaseModel):
    claim: str = Field(min_length=1)
    evidence: list[SourceReference] = Field(default_factory=list)
    is_extrapolation: bool = False


class PraxisResponse(BaseModel):
    consensus_core: list[str] = Field(default_factory=list)
    remaining_tensions: list[str] = Field(default_factory=list)
    critical_question: str = Field(min_length=1)

    @model_validator(mode="after")
    def require_content(self) -> "PraxisResponse":
        if not self.consensus_core and not self.remaining_tensions:
            raise ValueError("PraxisResponse must contain consensus or a remaining tension")
        return self


class ThesisSubmission(BaseModel):
    phase: Literal[DeliberationPhase.INDEPENDENT_THESIS] = DeliberationPhase.INDEPENDENT_THESIS
    mind: MindId
    position: str = Field(min_length=1)
    claims: list[str] = Field(min_length=1)
    assumptions: list[str] = Field(default_factory=list)
    unresolved_question: str = Field(min_length=1)
    supported_claims: list[SupportedClaim] = Field(default_factory=list)


class ChallengeSubmission(BaseModel):
    phase: Literal[DeliberationPhase.CHALLENGE] = DeliberationPhase.CHALLENGE
    mind: MindId
    strongest_point: str = Field(min_length=1)
    challenged_assumption: str = Field(min_length=1)
    objection: str = Field(min_length=1)
    question: str = Field(min_length=1)


class RevisionSubmission(BaseModel):
    phase: Literal[DeliberationPhase.REVISION] = DeliberationPhase.REVISION
    mind: MindId
    disposition: RevisionDisposition
    position: str = Field(min_length=1)
    changed_claims: list[str] = Field(default_factory=list)


class ConsensusProposalSubmission(BaseModel):
    phase: Literal[DeliberationPhase.CONSENSUS_PROPOSAL] = DeliberationPhase.CONSENSUS_PROPOSAL
    mind: MindId
    response: PraxisResponse


class CandidateRatification(BaseModel):
    candidate: MindId
    decision: RatificationDecision
    reason: str = Field(min_length=1)


class RatificationSubmission(BaseModel):
    phase: Literal[DeliberationPhase.RATIFICATION] = DeliberationPhase.RATIFICATION
    mind: MindId
    ballots: list[CandidateRatification] = Field(min_length=3, max_length=3)

    @model_validator(mode="after")
    def require_every_candidate_once(self) -> "RatificationSubmission":
        candidates = [ballot.candidate for ballot in self.ballots]
        if len(set(candidates)) != len(GOVERNED_MINDS) or set(candidates) != set(GOVERNED_MINDS):
            raise ValueError("ratification must evaluate each governed mind's candidate exactly once")
        return self


Submission = Annotated[
    Union[
        ThesisSubmission,
        ChallengeSubmission,
        RevisionSubmission,
        ConsensusProposalSubmission,
        RatificationSubmission,
    ],
    Field(discriminator="phase"),
]


class DeliberationState(BaseModel):
    question: str = Field(min_length=1)
    current_phase: DeliberationPhase = DeliberationPhase.INDEPENDENT_THESIS
    submissions: list[Submission] = Field(default_factory=list)
    completed: bool = False
    response: PraxisResponse | None = None
