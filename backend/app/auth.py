"""Who is calling? Verifies the Cognito access token sent as `Authorization: Bearer <token>`.

Same approach as spry (Lab 4): every /api call except /api/health needs a valid token.
The frontend can still show a public landing page; the data itself is only for signed-in users.
"""

from datetime import UTC, datetime
from functools import lru_cache
from typing import Annotated
from zoneinfo import ZoneInfo

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.dialects.postgresql import insert

from app.config import settings
from app.db import SessionDep
from app.models import User, UserVisit

LOCAL_USER = "local"  # the single user when auth is off (docker compose, tests)

_bearer = HTTPBearer(auto_error=False)


@lru_cache
def _jwks_client() -> jwt.PyJWKClient:
    # Downloads the user pool's public keys once and caches them (refetches on an unknown kid).
    return jwt.PyJWKClient(
        f"{settings.cognito_issuer}/.well-known/jwks.json", cache_keys=True, lifespan=3600
    )


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED, detail, headers={"WWW-Authenticate": "Bearer"}
    )


def verify_access_token(token: str) -> dict:
    """Signature (JWKS), expiry, issuer, token_use and client_id — or 401."""
    try:
        key = _jwks_client().get_signing_key_from_jwt(token).key
        claims = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=settings.cognito_issuer,
            options={"require": ["exp", "iss", "sub"], "verify_aud": False},
            leeway=30,
        )
    except jwt.PyJWTError as exc:
        raise _unauthorized(f"Invalid token: {exc}") from None
    # Cognito access tokens carry client_id instead of aud; ID tokens are not accepted here.
    if claims.get("token_use") != "access":
        raise _unauthorized("Expected an access token")
    if claims.get("client_id") != settings.cognito_client_id:
        raise _unauthorized("Token was issued for another app client")
    return claims


# Sync on purpose: FastAPI runs it in a thread, so a JWKS download never blocks the event loop.
def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> str:
    """The Cognito `sub` of the caller (stable per user)."""
    if not settings.cognito_issuer:
        return LOCAL_USER
    if credentials is None:
        raise _unauthorized("Sign in required")
    return verify_access_token(credentials.credentials)["sub"]


KYIV = ZoneInfo("Europe/Kyiv")


async def signed_in_user(user: Annotated[str, Depends(current_user)], session: SessionDep) -> str:
    """current_user + records that this user used the site today (for /api/stats)."""
    now = datetime.now(UTC)
    await session.execute(
        insert(User)
        .values(id=user, first_seen=now, last_seen=now)
        .on_conflict_do_update(index_elements=[User.id], set_={"last_seen": now})
    )
    await session.execute(
        insert(UserVisit)
        .values(user_id=user, day=now.astimezone(KYIV).date())
        .on_conflict_do_nothing()
    )
    await session.commit()
    return user


UserDep = Annotated[str, Depends(signed_in_user)]
