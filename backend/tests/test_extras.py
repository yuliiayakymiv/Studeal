"""University filter, deal conditions, event photos and usage stats."""

from datetime import UTC, date, datetime, timedelta

from httpx import AsyncClient

from app.models import Deal, Event, SavedDeal, User, UserVisit
from tests.test_api import _add


async def test_university_filter_for_deals_and_events(client: AsyncClient) -> None:
    soon = datetime.now(UTC) + timedelta(days=1)
    await _add(
        client,
        Deal(venue="UCU canteen", title="Lunch", category="food", university="ucu"),
        Deal(
            venue="Cafe A",
            title="-10% coffee",
            category="coffee",
            description="Weekdays 10:00-16:00, show your student ID",
        ),
        Event(title="UCU meetup", starts_at=soon, university="ucu", image_url="https://x/p.jpg"),
        Event(title="City concert", starts_at=soon),
    )

    ucu = (await client.get("/api/deals", params={"university": "UCU"})).json()
    assert [d["venue"] for d in ucu] == ["UCU canteen"]
    everyone = (await client.get("/api/deals")).json()
    assert len(everyone) == 2
    cafe = next(d for d in everyone if d["venue"] == "Cafe A")
    assert cafe["description"].startswith("Weekdays")

    ucu_events = (await client.get("/api/events", params={"university": "ucu"})).json()
    assert [e["title"] for e in ucu_events] == ["UCU meetup"]
    assert ucu_events[0]["image_url"] == "https://x/p.jpg"


async def test_stats_count_users_returns_and_saves(client: AsyncClient) -> None:
    empty = (await client.get("/api/stats")).json()
    assert empty == {
        "users_total": 0,
        "users_returned": 0,
        "users_active_7d": 0,
        "saved_total": 0,
        "top_saved": [],
    }

    # Signing in (any /api/me call) records the user and today's visit.
    assert (await client.get("/api/me")).status_code == 200
    await client.get("/api/me")  # same day twice = still one visit day

    # A second user who came back on another day and saved a deal.
    old = datetime.now(UTC) - timedelta(days=30)
    await _add(
        client,
        User(id="user-b", first_seen=old, last_seen=old),
        Deal(venue="Cafe A", title="-10% coffee", category="coffee"),
    )
    deal_id = (await client.get("/api/deals")).json()[0]["id"]
    await _add(
        client,
        UserVisit(user_id="user-b", day=date(2026, 1, 1)),
        UserVisit(user_id="user-b", day=date(2026, 1, 2)),
        SavedDeal(user_id="user-b", deal_id=deal_id),
    )
    assert (await client.post(f"/api/me/saved/{deal_id}")).status_code == 204

    stats = (await client.get("/api/stats")).json()
    assert stats["users_total"] == 2
    assert stats["users_returned"] == 1  # only user-b used it on 2+ days
    assert stats["users_active_7d"] == 1  # user-b was last seen a month ago
    assert stats["saved_total"] == 2
    assert stats["top_saved"] == [
        {"id": deal_id, "venue": "Cafe A", "title": "-10% coffee", "saves": 2}
    ]


async def test_search_deals_and_events(client: AsyncClient) -> None:
    soon = datetime.now(UTC) + timedelta(days=1)
    await _add(
        client,
        Deal(venue="Кав'ярня Зерно", title="Лате зі знижкою", category="coffee"),
        Deal(
            venue="Gym B",
            title="Student month",
            category="sport",
            description="Безлімітна кава після тренування",
        ),
        Deal(venue="Cinema", title="Tickets", category="cinema", address="вул. Кавова 5"),
        Deal(venue="Coworking", title="Day pass", category="coworking"),
        Event(title="Квіз у кав'ярні", starts_at=soon),
        Event(title="Concert", venue="КАВА club", starts_at=soon),
        Event(title="Lecture", starts_at=soon),
    )

    found = (await client.get("/api/deals", params={"q": "  КАВ "})).json()
    assert {d["venue"] for d in found} == {"Кав'ярня Зерно", "Gym B", "Cinema"}

    combined = (await client.get("/api/deals", params={"q": "кав", "category": "sport"})).json()
    assert [d["venue"] for d in combined] == ["Gym B"]

    assert len((await client.get("/api/deals", params={"q": ""})).json()) == 4  # empty = all

    events = (await client.get("/api/events", params={"q": "кав"})).json()
    assert {e["title"] for e in events} == {"Квіз у кав'ярні", "Concert"}
