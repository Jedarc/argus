from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt as pyjwt
import pytest

from api.security import (
    _JWT_ALGORITHM,
    _JWT_SECRET_KEY,
    create_access_token,
    hash_password,
    require_authenticated_user_ws,
    verify_password,
)


def test_hash_and_verify_password():
    hashed = hash_password("MyStr0ng!Pass")
    assert verify_password("MyStr0ng!Pass", hashed)
    assert not verify_password("WrongPassword1!", hashed)


def test_create_access_token_contains_version():
    token = create_access_token(token_version=7)
    payload = pyjwt.decode(token, _JWT_SECRET_KEY, algorithms=[_JWT_ALGORITHM])
    assert payload["sub"] == "argus"
    assert payload["tkv"] == 7


def test_valid_token_accepted():
    token = create_access_token(token_version=1)
    with patch("api.models.system_config.SystemConfig.get", return_value="1"):
        require_authenticated_user_ws(token, database_session=object())  # must not raise


def test_wrong_token_version_rejected():
    token = create_access_token(token_version=1)
    with patch("api.models.system_config.SystemConfig.get", return_value="2"):
        with pytest.raises(Exception) as exc_info:
            require_authenticated_user_ws(token, database_session=object())
    assert exc_info.value.status_code == 401


def test_expired_token_rejected():
    expired_payload = {
        "sub": "argus",
        "tkv": 1,
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
    }
    expired_token = pyjwt.encode(expired_payload, _JWT_SECRET_KEY, algorithm=_JWT_ALGORITHM)
    with pytest.raises(Exception) as exc_info:
        require_authenticated_user_ws(expired_token, database_session=object())
    assert exc_info.value.status_code == 401


def test_garbage_token_rejected():
    with pytest.raises(Exception) as exc_info:
        require_authenticated_user_ws("not.a.token", database_session=object())
    assert exc_info.value.status_code == 401


def test_empty_token_rejected():
    with pytest.raises(Exception) as exc_info:
        require_authenticated_user_ws("", database_session=object())
    assert exc_info.value.status_code == 401
