"""Studeal+: email subscribers about current deals at the venues they follow.

A deal matches a followed venue when the deal's venue contains what the user typed
(case-insensitive): "aroma" matches "Aroma Kava (Центр / Сихів / Привокзальна)".
Each deal is emailed to a user at most once (table deal_notifications).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.mailer import send_email
from app.models import Deal, DealNotification, FollowedVenue, Subscription

KYIV = ZoneInfo("Europe/Kyiv")


def _email_body(deals: list[Deal]) -> str:
    lines = ["Привіт! У закладах, за якими ви стежите, зараз є студентські знижки:", ""]
    for d in deals:
        line = f"• {d.venue}: {d.title}"
        if d.discount:
            line += f" ({d.discount})"
        if d.valid_until:
            line += f", діє до {d.valid_until:%d.%m.%Y}"
        lines.append(line)
        if d.address:
            lines.append(f"  {d.address}")
        lines.append(f"  {settings.site_url}/deals/{d.id}")
    lines += ["", "Studeal: знижки і події для студентів Львова", settings.site_url]
    return "\n".join(lines)


async def notify(session: AsyncSession, user_id: str | None = None) -> int:
    """Email every active subscriber (or just `user_id`) about new matching deals.

    Returns how many emails were sent.
    """
    today = datetime.now(KYIV).date()
    query = (
        select(Subscription, Deal)
        .join(FollowedVenue, FollowedVenue.user_id == Subscription.user_id)
        .join(
            Deal,
            func.lower(Deal.venue).contains(func.lower(func.trim(FollowedVenue.name))),
        )
        .outerjoin(
            DealNotification,
            and_(
                DealNotification.user_id == Subscription.user_id,
                DealNotification.deal_id == Deal.id,
            ),
        )
        .where(
            Subscription.active.is_(True),
            DealNotification.deal_id.is_(None),
            or_(Deal.valid_until.is_(None), Deal.valid_until >= today),
        )
        .order_by(Deal.venue, Deal.title)
    )
    if user_id is not None:
        query = query.where(Subscription.user_id == user_id)

    per_user: dict[str, tuple[Subscription, dict]] = {}
    for sub, deal in (await session.execute(query)).all():
        _, deals = per_user.setdefault(sub.user_id, (sub, {}))
        deals[deal.id] = deal  # one venue name can match the same deal twice

    sent = 0
    for sub, deals_by_id in per_user.values():
        deals = list(deals_by_id.values())
        subject = (
            f"Studeal: знижка в «{deals[0].venue}»"
            if len(deals) == 1
            else f"Studeal: {len(deals)} знижок у ваших закладах"
        )
        if await send_email(sub.email, subject, _email_body(deals)):
            await session.execute(
                insert(DealNotification)
                .values([{"user_id": sub.user_id, "deal_id": d.id} for d in deals])
                .on_conflict_do_nothing()
            )
            sent += 1
    await session.commit()
    return sent
