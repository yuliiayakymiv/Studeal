from datetime import date, timedelta

import pytest
from httpx import AsyncClient

from app import notify as notify_module
from app.db import get_session
from app.main import app
from app.models import Deal
from tests.test_api import _add


@pytest.fixture
def outbox(monkeypatch) -> list[tuple[str, str, str]]:
    sent: list[tuple[str, str, str]] = []

    async def fake_send(to: str, subject: str, body: str) -> bool:
        sent.append((to, subject, body))
        return True

    monkeypatch.setattr(notify_module, "send_email", fake_send)
    return sent


async def test_follow_needs_subscription(client: AsyncClient, outbox) -> None:
    state = (await client.get("/api/me/subscription")).json()
    assert state == {"active": False, "email": None, "price_usd": 5, "venues": []}
    response = await client.post("/api/me/subscription/venues", json={"name": "Aroma"})
    assert response.status_code == 402


async def test_subscribe_follow_and_email_once(client: AsyncClient, outbox) -> None:
    today = date.today()
    await _add(
        client,
        Deal(venue="Aroma Kava", title="-10% coffee", category="coffee", discount="-10%"),
        Deal(venue="Aroma Kava", title="Old", category="coffee", valid_until=today - timedelta(1)),
        Deal(venue="Gym B", title="Student month", category="sport"),
    )
    bad = await client.post("/api/me/subscription", json={"email": "not-an-email"})
    assert bad.status_code == 422

    state = (await client.post("/api/me/subscription", json={"email": "a@ucu.edu.ua"})).json()
    assert state["active"] and state["email"] == "a@ucu.edu.ua"

    state = (await client.post("/api/me/subscription/venues", json={"name": " aroma "})).json()
    assert [(v["name"], v["deals_now"]) for v in state["venues"]] == [("aroma", 1)]
    # A current deal already exists -> one email right away, the expired one is left out.
    assert len(outbox) == 1
    to, subject, body = outbox[0]
    assert to == "a@ucu.edu.ua" and "Aroma Kava" in subject and "-10% coffee" in body
    assert "Old" not in body

    # Following again or another follow without new deals sends nothing new.
    await client.post("/api/me/subscription/venues", json={"name": "Aroma"})
    await client.post("/api/me/subscription/venues", json={"name": "Pizza Nowhere"})
    assert len(outbox) == 1

    # A new deal at a followed venue (e.g. after `make seed`) -> a new email.
    await _add(client, Deal(venue="Pizza Nowhere Lviv", title="-20%", category="food"))
    gen = app.dependency_overrides[get_session]()
    session = await anext(gen)
    assert await notify_module.notify(session) == 1
    await gen.aclose()
    assert "Pizza Nowhere Lviv" in outbox[1][1]

    venue_id = state["venues"][0]["id"]
    assert (await client.delete(f"/api/me/subscription/venues/{venue_id}")).status_code == 204
    assert (await client.delete("/api/me/subscription")).status_code == 204
    state = (await client.get("/api/me/subscription")).json()
    assert not state["active"] and [v["name"] for v in state["venues"]] == ["Pizza Nowhere"]


async def test_venue_names_for_suggestions(client: AsyncClient) -> None:
    await _add(
        client,
        Deal(venue="B cafe", title="x", category="coffee"),
        Deal(venue="A gym", title="y", category="sport"),
        Deal(venue="A gym", title="z", category="sport"),
    )
    assert (await client.get("/api/deals/venues")).json() == ["A gym", "B cafe"]
