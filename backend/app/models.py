from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Deal(Base):
    """A student discount at a venue. Filled from docs/data/deals.csv by `make seed`."""

    __tablename__ = "deals"
    __table_args__ = (UniqueConstraint("venue", "title", name="uq_deals_venue_title"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    venue: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(300))
    category: Mapped[str] = mapped_column(String(50), index=True)
    discount: Mapped[str | None] = mapped_column(String(100))
    address: Mapped[str | None] = mapped_column(String(300))
    valid_until: Mapped[date | None] = mapped_column(Date)
    source_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Event(Base):
    """A student event. Filled from docs/data/events.csv by `make seed`."""

    __tablename__ = "events"
    __table_args__ = (UniqueConstraint("title", "starts_at", name="uq_events_title_starts_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    venue: Mapped[str | None] = mapped_column(String(200))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    address: Mapped[str | None] = mapped_column(String(300))
    price: Mapped[str | None] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SavedDeal(Base):
    """A deal a user saved. user_id = Cognito "sub" of the user."""

    __tablename__ = "saved_deals"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    deal_id: Mapped[int] = mapped_column(
        ForeignKey("deals.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
