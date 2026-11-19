import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from app.auth import UserDep
from app.db import SessionDep
from app.models import Deal
from app.schemas import DealOut

router = APIRouter(prefix="/deals", tags=["deals"])

KYIV = ZoneInfo("Europe/Kyiv")


@router.get("", response_model=list[DealOut])
async def list_deals(
    session: SessionDep,
    _user: UserDep,
    category: str | None = None,
    university: str | None = None,
    q: str | None = None,
    include_expired: bool = False,
) -> list[Deal]:
    """Current deals (no `valid_until`, or it is today or later in Kyiv). Filters can be combined:

    - `?category=coffee`
    - `?university=ucu` — only that university's places
    - `?q=кава` — search in venue, title, conditions and address (case-insensitive)
    - `?include_expired=true` — also deals whose `valid_until` has passed
    """
    query = select(Deal).order_by(Deal.venue, Deal.title)
    if not include_expired:
        today = datetime.now(KYIV).date()
        query = query.where(or_(Deal.valid_until.is_(None), Deal.valid_until >= today))
    if category:
        query = query.where(Deal.category == category)
    if university:
        query = query.where(Deal.university == university.lower())
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = query.where(
            or_(
                Deal.venue.ilike(pattern),
                Deal.title.ilike(pattern),
                Deal.description.ilike(pattern),
                Deal.address.ilike(pattern),
            )
        )
    return list(await session.scalars(query))


@router.get("/categories", response_model=list[str])
async def list_categories(session: SessionDep, _user: UserDep) -> list[str]:
    return list(await session.scalars(select(Deal.category).distinct().order_by(Deal.category)))


@router.get("/{deal_id}", response_model=DealOut)
async def get_deal(deal_id: uuid.UUID, session: SessionDep, _user: UserDep) -> Deal:
    deal = await session.get(Deal, deal_id)
    if deal is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Deal not found")
    return deal
