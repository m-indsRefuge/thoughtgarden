import pytest

from app.praxis.contracts import (
    CandidateRatification,
    ChallengeSubmission,
    ConsensusProposalSubmission,
    DeliberationPhase,
    MindId,
    PraxisResponse,
    RatificationDecision,
    RatificationSubmission,
    RevisionDisposition,
    RevisionSubmission,
    ThesisSubmission,
)
from app.praxis.state_machine import (
    DuplicateSubmissionError,
    PhaseMismatchError,
    new_deliberation,
    record_submission,
)


def thesis(mind: MindId) -> ThesisSubmission:
    return ThesisSubmission(
        mind=mind,
        position=f"{mind.value} position",
        claims=[f"{mind.value} claim"],
        assumptions=[f"{mind.value} assumption"],
        unresolved_question="What follows?",
    )


def challenge(mind: MindId) -> ChallengeSubmission:
    return ChallengeSubmission(
        mind=mind,
        strongest_point="A strong point",
        challenged_assumption="An assumption",
        objection="An objection",
        question="A question?",
    )


def revision(mind: MindId) -> RevisionSubmission:
    return RevisionSubmission(
        mind=mind,
        disposition=RevisionDisposition.REVISED,
        position=f"{mind.value} revised position",
        changed_claims=[f"{mind.value} changed claim"],
    )


def proposal(mind: MindId) -> ConsensusProposalSubmission:
    return ConsensusProposalSubmission(
        mind=mind,
        response=PraxisResponse(
            consensus_core=[f"{mind.value} proposed consensus"],
            remaining_tensions=[f"{mind.value} tension"],
            critical_question="What should be examined next?",
        ),
    )


def ratification(mind: MindId) -> RatificationSubmission:
    return RatificationSubmission(
        mind=mind,
        ballots=[
            CandidateRatification(
                candidate=candidate,
                decision=RatificationDecision.RATIFY,
                reason="Defensible from this framework.",
            )
            for candidate in MindId
        ],
    )


def test_new_deliberation_starts_at_independent_thesis() -> None:
    state = new_deliberation("What is consciousness?")

    assert state.question == "What is consciousness?"
    assert state.current_phase is DeliberationPhase.INDEPENDENT_THESIS
    assert state.completed is False
    assert state.submissions == []


def test_phase_advances_only_after_all_three_minds_submit() -> None:
    state = new_deliberation("What is consciousness?")

    state = record_submission(state, thesis(MindId.PLATONIC))
    state = record_submission(state, thesis(MindId.NIETZSCHEAN))
    assert state.current_phase is DeliberationPhase.INDEPENDENT_THESIS

    state = record_submission(state, thesis(MindId.FAUSTIAN))
    assert state.current_phase is DeliberationPhase.CHALLENGE


def test_duplicate_submission_from_same_mind_and_phase_is_rejected() -> None:
    state = new_deliberation("What is consciousness?")
    state = record_submission(state, thesis(MindId.PLATONIC))

    with pytest.raises(DuplicateSubmissionError):
        record_submission(state, thesis(MindId.PLATONIC))


def test_out_of_phase_submission_is_rejected() -> None:
    state = new_deliberation("What is consciousness?")
    early_revision = RevisionSubmission(
        mind=MindId.PLATONIC,
        disposition=RevisionDisposition.MAINTAINED,
        position="Still here",
        changed_claims=[],
    )

    with pytest.raises(PhaseMismatchError):
        record_submission(state, early_revision)


def test_challenge_phase_does_not_advance_after_one_submission() -> None:
    state = new_deliberation("What is consciousness?")
    for mind in MindId:
        state = record_submission(state, thesis(mind))

    state = record_submission(state, challenge(MindId.PLATONIC))

    assert state.current_phase is DeliberationPhase.CHALLENGE


def test_full_protocol_reaches_completion_only_after_three_ratifications() -> None:
    state = new_deliberation("What is consciousness?")

    phase_inputs = [
        (DeliberationPhase.INDEPENDENT_THESIS, thesis),
        (DeliberationPhase.CHALLENGE, challenge),
        (DeliberationPhase.REVISION, revision),
        (DeliberationPhase.CONSENSUS_PROPOSAL, proposal),
    ]

    for expected_phase, factory in phase_inputs:
        assert state.current_phase is expected_phase
        for mind in MindId:
            state = record_submission(state, factory(mind))
        assert state.completed is False

    assert state.current_phase is DeliberationPhase.RATIFICATION

    state = record_submission(state, ratification(MindId.PLATONIC))
    state = record_submission(state, ratification(MindId.NIETZSCHEAN))
    assert state.completed is False

    state = record_submission(state, ratification(MindId.FAUSTIAN))
    assert state.completed is True
    assert state.current_phase is DeliberationPhase.RATIFICATION
    assert len(state.submissions) == 15
