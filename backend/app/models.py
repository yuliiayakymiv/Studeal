import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Deal(Base):
    """A student discount at a venue. Filled from docs/data/deals.csv by `make seed`."""

    __tablename__ = "deals"
    __table_args__ = (UniqueConstraint("venue", "title", name="uq_deals_venue_title"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    venue: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(300))
    category: Mapped[str] = mapped_column(String(50), index=True)
    discount: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(300))
    valid_until: Mapped[date | None] = mapped_column(Date)
    source_url: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)  # link to a photo of the venue/offer
    description: Mapped[str | None] = mapped_column(Text)  # conditions: hours, what to show, etc.
    # One university only (e.g. "ucu" for the UCU canteen); empty = for everyone.
    university: Mapped[str | None] = mapped_column(String(20), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Event(Base):
    """A student event. Filled from docs/data/events.csv by `make seed`."""

    __tablename__ = "events"
    __table_args__ = (UniqueConstraint("title", "starts_at", name="uq_events_title_starts_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(300))
    venue: Mapped[str | None] = mapped_column(String(200))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    address: Mapped[str | None] = mapped_column(String(300))
    price: Mapped[str | None] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text)
    university: Mapped[str | None] = mapped_column(String(20), index=True)  # e.g. "ucu"
    category: Mapped[str | None] = mapped_column(String(50), index=True)  # e.g. "quiz", "concert"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SavedDeal(Base):
    """A deal a user saved. user_id = Cognito "sub" of the user."""

    __tablename__ = "saved_deals"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    deal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("deals.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class SavedEvent(Base):
    """An event a user saved. user_id = Cognito "sub" of the user."""

    __tablename__ = "saved_events"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    """Someone who signed in at least once (id = Cognito "sub"). Used for the usage stats."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserVisit(Base):
    """One row per user per day they used the site while signed in (to count who came back)."""

    __tablename__ = "user_visits"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    day: Mapped[date] = mapped_column(Date, primary_key=True)
