from datetime import datetime, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Inquiry
from app.praxis.contracts import DeliberationState
from app.praxis.state_machine import new_deliberation


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def create_inquiry(
    session: AsyncSession,
    *,
    title: str,
    question: str,
) -> Inquiry:
    state = new_deliberation(question)
    inquiry = Inquiry(
        title=title.strip(),
        question=question.strip(),
        state=state.model_dump(mode="json"),
    )
    session.add(inquiry)
    await session.commit()
    await session.refresh(inquiry)
    return inquiry


async def get_inquiry(session: AsyncSession, inquiry_id: int) -> Inquiry | None:
    return await session.get(Inquiry, inquiry_id)


async def list_inquiries(session: AsyncSession) -> list[Inquiry]:
    result = await session.exec(select(Inquiry).order_by(Inquiry.id.desc()))
    return list(result.all())


async def save_state(
    session: AsyncSession,
    *,
    inquiry: Inquiry,
    state: DeliberationState,
) -> Inquiry:
    inquiry.state = state.model_dump(mode="json")
    inquiry.updated_at = utc_now()
    session.add(inquiry)
    await session.commit()
    await session.refresh(inquiry)
    return inquiry
