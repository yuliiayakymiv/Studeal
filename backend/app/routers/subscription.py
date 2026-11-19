"""Studeal+ for $5: follow venues and get an email when they have a student discount.

The payment is a demo: POST /api/me/subscription turns it on, no money moves.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import UserDep
from app.db import SessionDep
from app.models import Deal, FollowedVenue, Subscription
from app.notify import KYIV, notify
from app.schemas import FollowedVenueOut, FollowIn, SubscribeIn, SubscriptionOut

PRICE_USD = 5

router = APIRouter(prefix="/me/subscription", tags=["subscription"])


async def _state(session: AsyncSession, user: str) -> SubscriptionOut:
    sub = await session.get(Subscription, user)
    venues = list(
        await session.scalars(
            select(FollowedVenue)
            .where(FollowedVenue.user_id == user)
            .order_by(FollowedVenue.created_at)
        )
    )
    today = datetime.now(KYIV).date()
    out = []
    for v in venues:
        count = await session.scalar(
            select(func.count())
            .select_from(Deal)
            .where(
                func.lower(Deal.venue).contains(func.lower(v.name)),
                or_(Deal.valid_until.is_(None), Deal.valid_until >= today),
            )
        )
        out.append(FollowedVenueOut(id=v.id, name=v.name, deals_now=count or 0))
    return SubscriptionOut(
        active=bool(sub and sub.active),
        email=sub.email if sub else None,
        price_usd=PRICE_USD,
        venues=out,
    )


async def _require_active(session: AsyncSession, user: str) -> None:
    sub = await session.get(Subscription, user)
    if not (sub and sub.active):
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "Studeal+ subscription required")


@router.get("", response_model=SubscriptionOut)
async def get_subscription(user: UserDep, session: SessionDep) -> SubscriptionOut:
    return await _state(session, user)


@router.post("", response_model=SubscriptionOut)
async def subscribe(body: SubscribeIn, user: UserDep, session: SessionDep) -> SubscriptionOut:
    """Demo payment of $5: turns Studeal+ on (or changes the email)."""
    await session.execute(
        insert(Subscription)
        .values(user_id=user, email=body.email, active=True)
        .on_conflict_do_update(
            index_elements=[Subscription.user_id], set_={"email": body.email, "active": True}
        )
    )
    await session.commit()
    await notify(session, user)  # venues followed before a pause get their emails now
    return await _state(session, user)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe(user: UserDep, session: SessionDep) -> Response:
    sub = await session.get(Subscription, user)
    if sub:
        sub.active = False
        await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/venues", response_model=SubscriptionOut)
async def follow_venue(body: FollowIn, user: UserDep, session: SessionDep) -> SubscriptionOut:
    """Follow a venue. If it already has a discount, the email goes out right away."""
    await _require_active(session, user)
    name = " ".join(body.name.split())
    if len(name) < 2:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Name is too short")
    already = await session.scalar(
        select(FollowedVenue.id).where(
            FollowedVenue.user_id == user, func.lower(FollowedVenue.name) == name.lower()
        )
    )
    if already is None:  # "Aroma" and "aroma" are the same venue
        await session.execute(
            insert(FollowedVenue).values(user_id=user, name=name).on_conflict_do_nothing()
        )
        await session.commit()
        await notify(session, user)
    return await _state(session, user)


@router.delete("/venues/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_venue(venue_id: uuid.UUID, user: UserDep, session: SessionDep) -> Response:
    await session.execute(
        delete(FollowedVenue).where(FollowedVenue.id == venue_id, FollowedVenue.user_id == user)
    )
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
