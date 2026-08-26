from app.praxis.consensus import resolve_consensus
from app.praxis.contracts import (
    CandidateRatification,
    ConsensusProposalSubmission,
    DeliberationPhase,
    MindId,
    PraxisResponse,
    RatificationDecision,
    RatificationSubmission,
)
from app.praxis.state_machine import new_deliberation


def proposal(mind: MindId, text: str) -> ConsensusProposalSubmission:
    return ConsensusProposalSubmission(
        mind=mind,
        response=PraxisResponse(
            consensus_core=[text],
            remaining_tensions=[f"{mind.value} tension"],
            critical_question=f"What follows from {mind.value}?",
        ),
    )


def ballot(
    voter: MindId,
    plato: RatificationDecision,
    nietzsche: RatificationDecision,
    faust: RatificationDecision,
) -> RatificationSubmission:
    return RatificationSubmission(
        mind=voter,
        ballots=[
            CandidateRatification(candidate=MindId.PLATONIC, decision=plato, reason="p"),
            CandidateRatification(candidate=MindId.NIETZSCHEAN, decision=nietzsche, reason="n"),
            CandidateRatification(candidate=MindId.FAUSTIAN, decision=faust, reason="f"),
        ],
    )


def completed_state():
    state = new_deliberation("What is consciousness?")
    state.current_phase = DeliberationPhase.RATIFICATION
    state.completed = True
    state.submissions = [
        proposal(MindId.PLATONIC, "Shared proposition P"),
        proposal(MindId.NIETZSCHEAN, "Shared proposition N"),
        proposal(MindId.FAUSTIAN, "Shared proposition F"),
    ]
    return state


def test_unanimously_admissible_candidate_becomes_praxis_response() -> None:
    state = completed_state()
    state.submissions.extend(
        [
            ballot(MindId.PLATONIC, RatificationDecision.RATIFY, RatificationDecision.REJECT, RatificationDecision.REJECT),
            ballot(MindId.NIETZSCHEAN, RatificationDecision.RATIFY, RatificationDecision.REJECT, RatificationDecision.REJECT),
            ballot(MindId.FAUSTIAN, RatificationDecision.RATIFY_WITH_RESERVATION, RatificationDecision.REJECT, RatificationDecision.REJECT),
        ]
    )

    response = resolve_consensus(state)

    assert response.consensus_core == ["Shared proposition P"]
    assert any("reservation" in tension.lower() for tension in response.remaining_tensions)


def test_no_unanimously_admissible_candidate_does_not_fabricate_consensus() -> None:
    state = completed_state()
    state.submissions.extend(
        [
            ballot(MindId.PLATONIC, RatificationDecision.RATIFY, RatificationDecision.REJECT, RatificationDecision.REJECT),
            ballot(MindId.NIETZSCHEAN, RatificationDecision.REJECT, RatificationDecision.RATIFY, RatificationDecision.REJECT),
            ballot(MindId.FAUSTIAN, RatificationDecision.REJECT, RatificationDecision.REJECT, RatificationDecision.RATIFY),
        ]
    )

    response = resolve_consensus(state)

    assert response.consensus_core == []
    assert response.remaining_tensions
    assert "unresolved" in response.critical_question.lower()
