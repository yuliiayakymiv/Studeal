"""Usage numbers for the demo report: how many people tried Studeal and how many came back.

Only totals, no personal data. A user counts once they open the site signed in (any /api/me call).
"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import func, select

from app.db import SessionDep
from app.models import Deal, SavedDeal, User, UserVisit
from app.schemas import StatsOut, TopDeal

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsOut)
async def stats(session: SessionDep) -> StatsOut:
    users_total = await session.scalar(select(func.count()).select_from(User))

    days_per_user = (
        select(UserVisit.user_id)
        .group_by(UserVisit.user_id)
        .having(func.count(UserVisit.day) >= 2)
        .subquery()
    )
    users_returned = await session.scalar(select(func.count()).select_from(days_per_user))

    week_ago = datetime.now(UTC) - timedelta(days=7)
    users_active_7d = await session.scalar(
        select(func.count()).select_from(User).where(User.last_seen >= week_ago)
    )

    saved_total = await session.scalar(select(func.count()).select_from(SavedDeal))

    saves = func.count(SavedDeal.user_id).label("saves")
    top = await session.execute(
        select(Deal.id, Deal.venue, Deal.title, saves)
        .join(SavedDeal, SavedDeal.deal_id == Deal.id)
        .group_by(Deal.id)
        .order_by(saves.desc(), Deal.id)
        .limit(5)
    )

    return StatsOut(
        users_total=users_total or 0,
        users_returned=users_returned or 0,
        users_active_7d=users_active_7d or 0,
        saved_total=saved_total or 0,
        top_saved=[TopDeal(id=r.id, venue=r.venue, title=r.title, saves=r.saves) for r in top],
    )
