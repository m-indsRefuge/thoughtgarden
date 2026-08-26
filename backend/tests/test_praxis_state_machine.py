import pytest

from app.praxis.contracts import (
    ChallengeSubmission,
    DeliberationPhase,
    MindId,
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

    state = record_submission(
        state,
        ChallengeSubmission(
            mind=MindId.PLATONIC,
            strongest_point="A strong point",
            challenged_assumption="An assumption",
            objection="An objection",
            question="A question?",
        ),
    )

    assert state.current_phase is DeliberationPhase.CHALLENGE
