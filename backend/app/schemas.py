import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    venue: str
    title: str
    category: str
    discount: str | None
    address: str | None
    valid_until: date | None
    source_url: str | None
    image_url: str | None
    description: str | None
    university: str | None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    venue: str | None
    starts_at: datetime
    address: str | None
    price: str | None
    source_url: str | None
    image_url: str | None
    university: str | None


class MeOut(BaseModel):
    id: str


class TopDeal(BaseModel):
    id: uuid.UUID
    venue: str
    title: str
    saves: int


class StatsOut(BaseModel):
    users_total: int  # signed in at least once
    users_returned: int  # used the site on 2+ different days
    users_active_7d: int  # signed in during the last 7 days
    saved_total: int  # deals saved, all users together
    top_saved: list[TopDeal]
