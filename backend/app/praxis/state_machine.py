"""Deterministic five-phase deliberation state machine."""

from app.praxis.contracts import (
    BOUNDED_PHASES,
    GOVERNED_MINDS,
    DeliberationPhase,
    DeliberationState,
    Submission,
)


class DeliberationError(ValueError):
    """Base error for invalid deliberation transitions."""


class PhaseMismatchError(DeliberationError):
    """Raised when a mind submits for a phase that is not active."""


class DuplicateSubmissionError(DeliberationError):
    """Raised when a mind submits twice in the same phase."""


class DeliberationCompletedError(DeliberationError):
    """Raised when a submission is added after completion."""


def new_deliberation(question: str) -> DeliberationState:
    return DeliberationState(question=question)


def _submissions_for_phase(state: DeliberationState, phase: DeliberationPhase) -> list[Submission]:
    return [submission for submission in state.submissions if submission.phase == phase]


def record_submission(state: DeliberationState, submission: Submission) -> DeliberationState:
    if state.completed:
        raise DeliberationCompletedError("deliberation is already complete")

    if submission.phase != state.current_phase:
        raise PhaseMismatchError(
            f"expected phase {state.current_phase.value}, received {submission.phase.value}"
        )

    if any(
        existing.phase == submission.phase and existing.mind == submission.mind
        for existing in state.submissions
    ):
        raise DuplicateSubmissionError(
            f"{submission.mind.value} already submitted for {submission.phase.value}"
        )

    next_state = state.model_copy(deep=True)
    next_state.submissions.append(submission)

    phase_submissions = _submissions_for_phase(next_state, next_state.current_phase)
    if len(phase_submissions) != len(GOVERNED_MINDS):
        return next_state

    if next_state.current_phase is DeliberationPhase.RATIFICATION:
        next_state.completed = True
        return next_state

    current_index = BOUNDED_PHASES.index(next_state.current_phase)
    next_state.current_phase = BOUNDED_PHASES[current_index + 1]
    return next_state
