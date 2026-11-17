from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from app.db import SessionDep
from app.models import Deal
from app.schemas import DealOut

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("", response_model=list[DealOut])
async def list_deals(
    session: SessionDep,
    category: str | None = None,
    university: str | None = None,
    q: str | None = None,
) -> list[Deal]:
    """All deals. Filters can be combined:

    - `?category=coffee`
    - `?university=ucu` — only that university's places
    - `?q=кава` — search in venue, title, conditions and address (case-insensitive)
    """
    query = select(Deal).order_by(Deal.venue, Deal.title)
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
async def list_categories(session: SessionDep) -> list[str]:
    return list(await session.scalars(select(Deal.category).distinct().order_by(Deal.category)))


@router.get("/{deal_id}", response_model=DealOut)
async def get_deal(deal_id: int, session: SessionDep) -> Deal:
    deal = await session.get(Deal, deal_id)
    if deal is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Deal not found")
    return deal
