import uuid

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from app.auth import UserDep
from app.db import SessionDep
from app.models import Deal, SavedDeal
from app.schemas import DealOut, MeOut

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=MeOut)
async def me(user: UserDep) -> MeOut:
    return MeOut(id=user)


@router.get("/saved", response_model=list[DealOut])
async def list_saved(user: UserDep, session: SessionDep) -> list[Deal]:
    query = (
        select(Deal)
        .join(SavedDeal, SavedDeal.deal_id == Deal.id)
        .where(SavedDeal.user_id == user)
        .order_by(SavedDeal.created_at.desc())
    )
    return list(await session.scalars(query))


@router.post("/saved/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def save_deal(deal_id: uuid.UUID, user: UserDep, session: SessionDep) -> Response:
    if await session.get(Deal, deal_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Deal not found")
    await session.execute(
        insert(SavedDeal).values(user_id=user, deal_id=deal_id).on_conflict_do_nothing()
    )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/saved/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_deal(deal_id: uuid.UUID, user: UserDep, session: SessionDep) -> Response:
    await session.execute(
        delete(SavedDeal).where(SavedDeal.user_id == user, SavedDeal.deal_id == deal_id)
    )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
