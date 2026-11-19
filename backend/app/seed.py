"""Load deals and events from CSV files into the database. Safe to re-run.

Files (one header row, UTF-8, exported from Google Sheets: File → Download → CSV):
  docs/data/deals.csv   venue,title,category,discount,address,valid_until,source_url
                        [,image_url,description,university]
  docs/data/events.csv  title,venue,starts_at,address,price,source_url[,image_url,university]

A row with the same deal (venue + title) or event (title + starts_at) is updated, not duplicated.
Dates: valid_until = 2026-12-31 (or empty), starts_at = 2026-11-20 19:00 (Kyiv time).

Run: make seed
"""

import asyncio
import csv
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import delete, tuple_
from sqlalchemy.dialects.postgresql import insert

from app.config import settings
from app.db import SessionLocal, engine
from app.models import Deal, Event

KYIV = ZoneInfo("Europe/Kyiv")

DEAL_FIELDS = [
    "venue",
    "title",
    "category",
    "discount",
    "address",
    "valid_until",
    "source_url",
    "image_url",
    "description",
    "university",
]
EVENT_FIELDS = [
    "title",
    "venue",
    "starts_at",
    "address",
    "price",
    "source_url",
    "image_url",
    "university",
    "category"
]
# May be left out of the CSV entirely.
OPTIONAL_COLUMNS = {"image_url", "description", "university", "category"}

def _clean(value: str | None) -> str | None:
    value = (value or "").strip()
    return value or None


def _read(path: Path, fields: list[str]) -> list[dict]:
    if not path.exists():
        print(f"skip: {path} not found")
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = set(fields) - set(reader.fieldnames or []) - OPTIONAL_COLUMNS
        if missing:
            sys.exit(f"{path.name}: missing columns {sorted(missing)}")
        return [{k: _clean(row.get(k)) for k in fields} for row in reader if any(row.values())]


def _parse_deal(row: dict, line: int) -> dict:
    if not (row["venue"] and row["title"] and row["category"]):
        sys.exit(f"deals.csv line {line}: venue, title and category are required")
    if row["valid_until"]:
        row["valid_until"] = date.fromisoformat(row["valid_until"])
    row["category"] = row["category"].lower()
    row["university"] = row["university"] and row["university"].lower()
    return row


def _parse_event(row: dict, line: int) -> dict:
    if not (row["title"] and row["starts_at"]):
        sys.exit(f"events.csv line {line}: title and starts_at are required")
    starts = datetime.fromisoformat(row["starts_at"])
    row["starts_at"] = starts if starts.tzinfo else starts.replace(tzinfo=KYIV)
    row["university"] = row["university"] and row["university"].lower()
    row["category"] = row["category"] and row["category"].lower()
    return row


async def seed(seed_dir: Path = settings.seed_dir) -> tuple[int, int]:
    deals = [_parse_deal(r, i) for i, r in enumerate(_read(seed_dir / "deals.csv", DEAL_FIELDS), 2)]
    events = [
        _parse_event(r, i) for i, r in enumerate(_read(seed_dir / "events.csv", EVENT_FIELDS), 2)
    ]

    async with SessionLocal() as session:
        if deals:
            stmt = insert(Deal).values(deals)
            await session.execute(
                stmt.on_conflict_do_update(
                    constraint="uq_deals_venue_title",
                    set_={f: stmt.excluded[f] for f in DEAL_FIELDS},
                )
            )
            await session.execute(
                delete(Deal).where(
                    tuple_(Deal.venue, Deal.title).not_in(
                        [(d["venue"], d["title"]) for d in deals]
                    )
                )
            )
        if events:
            stmt = insert(Event).values(events)
            await session.execute(
                stmt.on_conflict_do_update(
                    constraint="uq_events_title_starts_at",
                    set_={f: stmt.excluded[f] for f in EVENT_FIELDS},
                )
            )
        await session.commit()
    return len(deals), len(events)


async def main() -> None:
    deals, events = await seed()
    await engine.dispose()
    print(f"seeded {deals} deals and {events} events from {settings.seed_dir}")


if __name__ == "__main__":
    asyncio.run(main())
