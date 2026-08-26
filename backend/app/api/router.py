from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.models import Inquiry
from app.praxis.consensus import ConsensusNotReadyError, resolve_consensus
from app.praxis.contracts import DeliberationState, Submission
from app.praxis.state_machine import DeliberationError, record_submission
from app.repositories import inquiries as inquiry_repository


router = APIRouter()


class InquiryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    question: str = Field(min_length=1, max_length=10_000)


class InquiryView(BaseModel):
    id: int
    title: str
    question: str
    created_at: datetime
    updated_at: datetime
    state: DeliberationState


def to_view(inquiry: Inquiry) -> InquiryView:
    if inquiry.id is None:
        raise ValueError("persisted inquiry is missing an id")
    return InquiryView(
        id=inquiry.id,
        title=inquiry.title,
        question=inquiry.question,
        created_at=inquiry.created_at,
        updated_at=inquiry.updated_at,
        state=DeliberationState.model_validate(inquiry.state),
    )


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "engine": "praxis-v2"}


@router.post("/inquiries", response_model=InquiryView, status_code=status.HTTP_201_CREATED)
async def create_inquiry(
    inquiry_in: InquiryCreate,
    session: AsyncSession = Depends(get_session),
) -> InquiryView:
    inquiry = await inquiry_repository.create_inquiry(
        session,
        title=inquiry_in.title,
        question=inquiry_in.question,
    )
    return to_view(inquiry)


@router.get("/inquiries", response_model=list[InquiryView])
async def list_inquiries(
    session: AsyncSession = Depends(get_session),
) -> list[InquiryView]:
    inquiries = await inquiry_repository.list_inquiries(session)
    return [to_view(inquiry) for inquiry in inquiries]


@router.get("/inquiries/{inquiry_id}", response_model=InquiryView)
async def get_inquiry(
    inquiry_id: int,
    session: AsyncSession = Depends(get_session),
) -> InquiryView:
    inquiry = await inquiry_repository.get_inquiry(session, inquiry_id)
    if inquiry is None:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    return to_view(inquiry)


@router.post("/inquiries/{inquiry_id}/submissions", response_model=InquiryView)
async def submit_deliberation_turn(
    inquiry_id: int,
    submission: Submission,
    session: AsyncSession = Depends(get_session),
) -> InquiryView:
    inquiry = await inquiry_repository.get_inquiry(session, inquiry_id)
    if inquiry is None:
        raise HTTPException(status_code=404, detail="Inquiry not found")

    state = DeliberationState.model_validate(inquiry.state)
    try:
        state = record_submission(state, submission)
        if state.completed:
            state.response = resolve_consensus(state)
    except (DeliberationError, ConsensusNotReadyError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    inquiry = await inquiry_repository.save_state(session, inquiry=inquiry, state=state)
    return to_view(inquiry)
