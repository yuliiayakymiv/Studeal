"""Auth on (Cognito configured): /api/me needs a valid access token. Same checks as spry."""

import time
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import AsyncClient

from app import auth
from app.config import settings

ISSUER = "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_TEST"
CLIENT_ID = "test-client"
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def make_token(key=KEY, **overrides) -> str:
    claims = {
        "sub": "user-a",
        "iss": ISSUER,
        "client_id": CLIENT_ID,
        "token_use": "access",
        "exp": int(time.time()) + 600,
    } | overrides
    return jwt.encode(claims, key, algorithm="RS256", headers={"kid": "k1"})


@pytest.fixture
def cognito(monkeypatch):
    """Auth on, with the JWKS download replaced by our test key."""
    monkeypatch.setattr(settings, "cognito_issuer", ISSUER)
    monkeypatch.setattr(settings, "cognito_client_id", CLIENT_ID)
    stub = SimpleNamespace(
        get_signing_key_from_jwt=lambda _t: SimpleNamespace(key=KEY.public_key())
    )
    monkeypatch.setattr(auth, "_jwks_client", lambda: stub)


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_public_endpoints_need_no_token(client: AsyncClient, cognito) -> None:
    for path in ("/api/health", "/api/deals", "/api/events"):
        assert (await client.get(path)).status_code == 200


async def test_me_without_token_is_401(client: AsyncClient, cognito) -> None:
    for path in ("/api/me", "/api/me/saved"):
        assert (await client.get(path)).status_code == 401


async def test_valid_token_returns_sub(client: AsyncClient, cognito) -> None:
    response = await client.get("/api/me", headers=bearer(make_token()))
    assert response.status_code == 200
    assert response.json() == {"id": "user-a"}


@pytest.mark.parametrize(
    "token",
    [
        make_token(key=OTHER_KEY),  # wrong signature
        make_token(exp=int(time.time()) - 3600),  # expired
        make_token(iss="https://evil.example.com"),  # wrong issuer
        make_token(client_id="other-client"),  # another app
        make_token(token_use="id"),  # ID token instead of access token
    ],
)
async def test_bad_tokens_are_401(client: AsyncClient, cognito, token: str) -> None:
    assert (await client.get("/api/me", headers=bearer(token))).status_code == 401


async def test_users_see_only_their_saved_deals(client: AsyncClient, cognito) -> None:
    from app.models import Deal
    from tests.test_api import _add

    await _add(client, Deal(venue="Cafe A", title="-10% coffee", category="coffee"))
    deal_id = (await client.get("/api/deals")).json()[0]["id"]

    a = bearer(make_token(sub="user-a"))
    b = bearer(make_token(sub="user-b"))
    assert (await client.post(f"/api/me/saved/{deal_id}", headers=a)).status_code == 204
    assert len((await client.get("/api/me/saved", headers=a)).json()) == 1
    assert (await client.get("/api/me/saved", headers=b)).json() == []
