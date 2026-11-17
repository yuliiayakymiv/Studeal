from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import or_, select

from app.db import SessionDep
from app.models import Event
from app.schemas import EventOut

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventOut])
async def list_events(
    session: SessionDep,
    include_past: bool = False,
    university: str | None = None,
    q: str | None = None,
) -> list[Event]:
    """Upcoming events, soonest first (started in the last 6 hours still counts).

    `?university=ucu` — only events of that university; `?q=квіз` — search in title and venue.
    """
    query = select(Event).order_by(Event.starts_at)
    if university:
        query = query.where(Event.university == university.lower())
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = query.where(or_(Event.title.ilike(pattern), Event.venue.ilike(pattern)))
    if not include_past:
        query = query.where(Event.starts_at >= datetime.now(UTC) - timedelta(hours=6))
    return list(await session.scalars(query))
