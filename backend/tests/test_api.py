import uuid
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from httpx import AsyncClient

from app import seed as seed_module
from app.db import get_session
from app.main import app
from app.models import Deal, Event


async def _add(client: AsyncClient, *rows) -> None:
    """Insert rows through the same session the API uses in tests."""
    session_gen = app.dependency_overrides[get_session]()
    session = await anext(session_gen)
    session.add_all(rows)
    await session.commit()
    await session_gen.aclose()


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_deals_list_filter_and_get(client: AsyncClient) -> None:
    await _add(
        client,
        Deal(venue="Cafe A", title="-10% coffee", category="coffee", discount="-10%"),
        Deal(
            venue="Gym B", title="Student month", category="sport", valid_until=date(2026, 12, 31)
        ),
    )

    all_deals = (await client.get("/api/deals")).json()
    assert [d["venue"] for d in all_deals] == ["Cafe A", "Gym B"]

    sport = (await client.get("/api/deals", params={"category": "sport"})).json()
    assert len(sport) == 1 and sport[0]["valid_until"] == "2026-12-31"

    assert (await client.get("/api/deals/categories")).json() == ["coffee", "sport"]

    one = await client.get(f"/api/deals/{all_deals[0]['id']}")
    assert one.status_code == 200 and one.json()["title"] == "-10% coffee"
    assert (await client.get(f"/api/deals/{uuid.uuid4()}")).status_code == 404
    assert (await client.get("/api/deals/123")).status_code == 422  # ids are UUIDs, as in spry


async def test_expired_deals_are_hidden(client: AsyncClient) -> None:
    today = date.today()
    await _add(
        client,
        Deal(venue="Old", title="Ended", category="coffee", valid_until=today - timedelta(days=2)),
        Deal(
            venue="Now",
            title="Ends later",
            category="coffee",
            valid_until=today + timedelta(days=5),
        ),
        Deal(venue="Open", title="No end date", category="coffee"),
    )
    current = (await client.get("/api/deals")).json()
    assert [d["venue"] for d in current] == ["Now", "Open"]
    everything = (await client.get("/api/deals", params={"include_expired": "true"})).json()
    assert len(everything) == 3


async def test_events_upcoming_only(client: AsyncClient) -> None:
    now = datetime.now(UTC)
    await _add(
        client,
        Event(title="Old talk", starts_at=now - timedelta(days=3)),
        Event(title="Concert", starts_at=now + timedelta(days=2)),
    )
    upcoming = (await client.get("/api/events")).json()
    assert [e["title"] for e in upcoming] == ["Concert"]
    everything = (await client.get("/api/events", params={"include_past": "true"})).json()
    assert len(everything) == 2


async def test_save_and_unsave_deal(client: AsyncClient) -> None:
    await _add(client, Deal(venue="Cafe A", title="-10% coffee", category="coffee"))
    deal_id = (await client.get("/api/deals")).json()[0]["id"]

    assert (await client.get("/api/me")).json() == {"id": "local"}  # auth off locally
    assert (await client.post(f"/api/me/saved/{deal_id}")).status_code == 204
    assert (await client.post(f"/api/me/saved/{deal_id}")).status_code == 204  # idempotent
    assert [d["id"] for d in (await client.get("/api/me/saved")).json()] == [deal_id]

    assert (await client.delete(f"/api/me/saved/{deal_id}")).status_code == 204
    assert (await client.get("/api/me/saved")).json() == []
    assert (await client.post(f"/api/me/saved/{uuid.uuid4()}")).status_code == 404


async def test_seed_from_csv_is_rerunnable(
    client: AsyncClient, tmp_path: Path, monkeypatch
) -> None:
    (tmp_path / "deals.csv").write_text(
        "venue,title,category,discount,address,valid_until,source_url\n"
        "Cafe A,-10% coffee,Coffee,-10%,Street 1,2026-12-31,https://example.com\n",
        encoding="utf-8",
    )
    (tmp_path / "events.csv").write_text(
        "title,venue,starts_at,address,price,source_url\n"
        "Concert,Club,2030-01-10 19:00,Street 2,100 UAH,\n",
        encoding="utf-8",
    )
    sessionmaker = app.dependency_overrides[get_session]
    monkeypatch.setattr(seed_module, "SessionLocal", _session_factory(sessionmaker))

    assert await seed_module.seed(tmp_path) == (1, 1)
    assert await seed_module.seed(tmp_path) == (1, 1)  # second run updates, no duplicates

    deals = (await client.get("/api/deals")).json()
    assert len(deals) == 1 and deals[0]["category"] == "coffee"
    assert deals[0]["image_url"] is None  # image_url column is optional in the CSV
    events = (await client.get("/api/events")).json()
    assert len(events) == 1 and events[0]["starts_at"].startswith("2030-01-10T17:00")  # Kyiv → UTC


def _session_factory(override):
    """Wrap the test session override as an `async with` factory like SessionLocal."""

    class _Ctx:
        async def __aenter__(self):
            self._gen = override()
            return await anext(self._gen)

        async def __aexit__(self, *exc):
            await self._gen.aclose()

    return _Ctx
