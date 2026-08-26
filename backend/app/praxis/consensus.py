"""Deterministic ratification-based Praxis response resolution."""

from app.praxis.contracts import (
    GOVERNED_MINDS,
    ConsensusProposalSubmission,
    DeliberationState,
    MindId,
    PraxisResponse,
    RatificationDecision,
    RatificationSubmission,
)


class ConsensusNotReadyError(ValueError):
    """Raised when consensus is requested before ratification is complete."""


def _proposals(state: DeliberationState) -> dict[MindId, ConsensusProposalSubmission]:
    return {
        submission.mind: submission
        for submission in state.submissions
        if isinstance(submission, ConsensusProposalSubmission)
    }


def _ratifications(state: DeliberationState) -> dict[MindId, RatificationSubmission]:
    return {
        submission.mind: submission
        for submission in state.submissions
        if isinstance(submission, RatificationSubmission)
    }


def resolve_consensus(state: DeliberationState) -> PraxisResponse:
    if not state.completed:
        raise ConsensusNotReadyError("ratification phase is not complete")

    proposals = _proposals(state)
    ratifications = _ratifications(state)
    if set(proposals) != set(GOVERNED_MINDS) or set(ratifications) != set(GOVERNED_MINDS):
        raise ConsensusNotReadyError("three proposals and three ratification submissions are required")

    admissible: list[tuple[int, int, MindId, list[str]]] = []
    for order, candidate in enumerate(GOVERNED_MINDS):
        exact_ratifies = 0
        reservations: list[str] = []
        rejected = False

        for voter in GOVERNED_MINDS:
            ballot = next(
                item for item in ratifications[voter].ballots if item.candidate == candidate
            )
            if ballot.decision is RatificationDecision.REJECT:
                rejected = True
                break
            if ballot.decision is RatificationDecision.RATIFY:
                exact_ratifies += 1
            else:
                reservations.append(f"{voter.value} reservation: {ballot.reason}")

        if not rejected:
            admissible.append((exact_ratifies, -order, candidate, reservations))

    if not admissible:
        tensions = ["No candidate Praxis response achieved unanimous ratification."]
        for mind in GOVERNED_MINDS:
            for tension in proposals[mind].response.remaining_tensions:
                labelled = f"{mind.value}: {tension}"
                if labelled not in tensions:
                    tensions.append(labelled)
        return PraxisResponse(
            consensus_core=[],
            remaining_tensions=tensions,
            critical_question="Which unresolved tension should the inquiry examine next?",
        )

    _, _, selected_mind, reservations = max(admissible, key=lambda item: (item[0], item[1]))
    selected = proposals[selected_mind].response.model_copy(deep=True)
    for reservation in reservations:
        if reservation not in selected.remaining_tensions:
            selected.remaining_tensions.append(reservation)
    return selected
