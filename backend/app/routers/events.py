from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import select

from app.db import SessionDep
from app.models import Event
from app.schemas import EventOut

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventOut])
async def list_events(session: SessionDep, include_past: bool = False) -> list[Event]:
    """Upcoming events, soonest first (events that started in the last 6 hours still count)."""
    query = select(Event).order_by(Event.starts_at)
    if not include_past:
        query = query.where(Event.starts_at >= datetime.now(UTC) - timedelta(hours=6))
    return list(await session.scalars(query))
