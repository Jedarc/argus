from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from api.database import get_database_session
from api.security import (
    create_access_token,
    hash_password,
    require_authenticated_user,
    verify_password,
)
from api.validators import validate_password_strength

router = APIRouter(prefix="/auth", tags=["auth"])

_COOKIE_NAME = "access_token"
_COOKIE_OPTIONS = {
    "httponly": True,
    "secure": True,       # Requires HTTPS — set to False only in local dev
    "samesite": "strict",
    "max_age": None,      # Session cookie by default; overridden on login with JWT_EXPIRY_HOURS
}

# Generic message used for all credential failures to prevent user enumeration.
_INVALID_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
)


class SetupRequest(BaseModel):
    password: str
    password_confirm: str

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: str) -> str:
        validate_password_strength(value)
        return value

    @field_validator("password_confirm")
    @classmethod
    def passwords_must_match(cls, value: str, info) -> str:
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Passwords do not match")
        return value


class LoginRequest(BaseModel):
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_must_be_strong(cls, value: str) -> str:
        validate_password_strength(value)
        return value


@router.get("/status")
def get_auth_status(database_session: Session = Depends(get_database_session)):
    """
    Returns whether first-run setup has been completed.
    Safe to call unauthenticated — reveals only a boolean, no sensitive data.
    """
    raise NotImplementedError


@router.post("/setup", status_code=status.HTTP_201_CREATED)
def setup(request: SetupRequest, database_session: Session = Depends(get_database_session)):
    """
    First-run only. Hashes and stores the password in system_config.
    Returns 404 (not found) if a password is already configured — the endpoint
    effectively ceases to exist after setup, giving no information to an attacker.
    """
    raise NotImplementedError


@router.post("/login")
def login(
    raw_request: Request,
    request: LoginRequest,
    response: Response,
    database_session: Session = Depends(get_database_session),
):
    """
    Rate-limited to 10 attempts per minute per IP.
    Returns the same error for wrong password and setup-not-done to prevent enumeration.
    Sets a signed JWT in an httpOnly + Secure + SameSite=Strict cookie on success.
    """
    raise NotImplementedError


@router.post("/logout", dependencies=[Depends(require_authenticated_user)])
def logout(response: Response):
    """Clears the auth cookie. Requires an active session."""
    response.delete_cookie(_COOKIE_NAME, httponly=True, secure=True, samesite="strict")
    return {"detail": "Logged out"}


@router.post("/change-password", dependencies=[Depends(require_authenticated_user)])
def change_password(
    request: ChangePasswordRequest,
    database_session: Session = Depends(get_database_session),
):
    """
    Verifies current password before accepting the new one.
    On success, increments token_version in system_config, immediately
    invalidating all existing sessions including the current one.
    The client must log in again with the new password.
    """
    raise NotImplementedError
