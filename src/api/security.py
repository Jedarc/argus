import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
import jwt
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_database_session

_JWT_ALGORITHM = "HS256"
_JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
_JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))

_CREDENTIAL_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
_SESSION_EXPIRED_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Session expired or invalidated",
    headers={"WWW-Authenticate": "Bearer"},
)


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(token_version: int) -> str:
    payload = {
        "sub": "argus",
        "tkv": token_version,
        "exp": datetime.now(timezone.utc) + timedelta(hours=_JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, _JWT_SECRET_KEY, algorithm=_JWT_ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, _JWT_SECRET_KEY, algorithms=[_JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise _SESSION_EXPIRED_ERROR
    except jwt.InvalidTokenError:
        raise _CREDENTIAL_ERROR


def require_authenticated_user(
    access_token: Annotated[str | None, Cookie()] = None,
    database_session: Session = Depends(get_database_session),
) -> None:
    if access_token is None:
        raise _CREDENTIAL_ERROR

    payload = _decode_token(access_token)

    # Late import avoids circular dependency before models are defined.
    from api.models.system_config import SystemConfig  # noqa: PLC0415

    stored_version = SystemConfig.get(database_session, "token_version")
    if stored_version is None or int(stored_version) != payload.get("tkv"):
        raise _SESSION_EXPIRED_ERROR


def require_authenticated_user_ws(token: str, database_session: Session) -> None:
    """
    Validates a JWT passed as ?token= query param for WebSocket connections.
    httpOnly cookies are not forwarded on WS upgrades, so the token must be
    passed explicitly and validated here before the connection is accepted.
    """
    if not token:
        raise _CREDENTIAL_ERROR

    payload = _decode_token(token)

    from api.models.system_config import SystemConfig  # noqa: PLC0415

    stored_version = SystemConfig.get(database_session, "token_version")
    if stored_version is None or int(stored_version) != payload.get("tkv"):
        raise _SESSION_EXPIRED_ERROR
