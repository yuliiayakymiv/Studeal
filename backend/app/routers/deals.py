from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.db import SessionDep
from app.models import Deal
from app.schemas import DealOut

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("", response_model=list[DealOut])
async def list_deals(session: SessionDep, category: str | None = None) -> list[Deal]:
    query = select(Deal).order_by(Deal.venue, Deal.title)
    if category:
        query = query.where(Deal.category == category)
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
