from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import or_, select

from app.auth import UserDep
from app.db import SessionDep
from app.models import Event
from app.schemas import EventOut

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventOut])
async def list_events(
    session: SessionDep,
    _user: UserDep,
    include_past: bool = False,
    category: str | None = None,
    university: str | None = None,
    q: str | None = None,
) -> list[Event]:
    """Upcoming events, soonest first (started in the last 6 hours still counts).

    - `?category=quiz` — only that category
    - `?university=ucu` — only events of that university
    - `?q=квіз` — search in title and venue
    """
    query = select(Event).order_by(Event.starts_at)
    if category:
        query = query.where(Event.category == category.lower())
    if university:
        query = query.where(Event.university == university.lower())
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = query.where(or_(Event.title.ilike(pattern), Event.venue.ilike(pattern)))
    if not include_past:
        query = query.where(Event.starts_at >= datetime.now(UTC) - timedelta(hours=6))
    return list(await session.scalars(query))


@router.get("/categories", response_model=list[str])
async def list_categories(session: SessionDep, _user: UserDep) -> list[str]:
    query = (
        select(Event.category)
        .where(Event.category.is_not(None))
        .distinct()
        .order_by(Event.category)
    )
    return list(await session.scalars(query))
