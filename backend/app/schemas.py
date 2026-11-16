from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    venue: str
    title: str
    category: str
    discount: str | None
    address: str | None
    valid_until: date | None
    source_url: str | None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    venue: str | None
    starts_at: datetime
    address: str | None
    price: str | None
    source_url: str | None


class MeOut(BaseModel):
    id: str
