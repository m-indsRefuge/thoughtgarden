from pathlib import Path

import pytest
from pydantic import ValidationError

from app.praxis.contracts import (
    BOUNDED_PHASES,
    GOVERNED_MINDS,
    ChallengeSubmission,
    DeliberationPhase,
    MindId,
    PraxisResponse,
    RatificationDecision,
    RevisionDisposition,
    RevisionSubmission,
    ThesisSubmission,
)


def test_praxis_has_exactly_three_governed_minds() -> None:
    assert GOVERNED_MINDS == (
        MindId.PLATONIC,
        MindId.NIETZSCHEAN,
        MindId.FAUSTIAN,
    )


def test_protocol_has_exactly_five_ordered_phases() -> None:
    assert BOUNDED_PHASES == (
        DeliberationPhase.INDEPENDENT_THESIS,
        DeliberationPhase.CHALLENGE,
        DeliberationPhase.REVISION,
        DeliberationPhase.CONSENSUS_PROPOSAL,
        DeliberationPhase.RATIFICATION,
    )


def test_praxis_response_requires_a_critical_question() -> None:
    with pytest.raises(ValidationError):
        PraxisResponse(
            consensus_core=["A defensible claim."],
            remaining_tensions=[],
            critical_question="",
        )


def test_revision_disposition_is_categorical() -> None:
    assert {item.value for item in RevisionDisposition} == {
        "maintained",
        "revised",
        "partially_conceded",
        "withdrawn",
    }


def test_ratification_is_not_a_numeric_score() -> None:
    assert {item.value for item in RatificationDecision} == {
        "ratify",
        "ratify_with_reservation",
        "reject",
    }


def test_phase_submissions_have_explicit_shapes() -> None:
    thesis = ThesisSubmission(
        mind=MindId.PLATONIC,
        position="A position",
        claims=["A claim"],
        assumptions=["An assumption"],
        unresolved_question="What remains unclear?",
    )
    challenge = ChallengeSubmission(
        mind=MindId.NIETZSCHEAN,
        strongest_point="A strong point",
        challenged_assumption="An assumption",
        objection="An objection",
        question="Why accept the premise?",
    )
    revision = RevisionSubmission(
        mind=MindId.FAUSTIAN,
        disposition=RevisionDisposition.REVISED,
        position="A revised position",
        changed_claims=["A changed claim"],
    )

    assert thesis.phase is DeliberationPhase.INDEPENDENT_THESIS
    assert challenge.phase is DeliberationPhase.CHALLENGE
    assert revision.phase is DeliberationPhase.REVISION


def test_all_three_soul_contracts_exist_and_reject_impersonation() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    paths = [
        backend_root / "app" / "praxis" / "minds" / "plato" / "soul.md",
        backend_root / "app" / "praxis" / "minds" / "nietzsche" / "soul.md",
        backend_root / "app" / "praxis" / "minds" / "faust" / "soul.md",
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "ThoughtGarden" in text
        assert "not impersonate" in text
