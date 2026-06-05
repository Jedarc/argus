from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class SetupRequest(BaseModel):
    password: str
    password_confirm: str


class LoginRequest(BaseModel):
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.get("/status")
def get_auth_status():
    """Returns whether first-run setup has been completed."""
    raise NotImplementedError


@router.post("/setup", status_code=status.HTTP_201_CREATED)
def setup(request: SetupRequest):
    """
    First-run only. Stores bcrypt hash of the password in system_config.
    Permanently disabled once a password is configured.
    """
    raise NotImplementedError


@router.post("/login")
def login(request: LoginRequest, response: Response):
    """Verifies password and sets a signed JWT in an httpOnly cookie."""
    raise NotImplementedError


@router.post("/logout")
def logout(response: Response):
    """Clears the auth cookie."""
    raise NotImplementedError


@router.post("/change-password")
def change_password(request: ChangePasswordRequest):
    """
    Changes the password and increments token_version,
    invalidating all existing sessions.
    """
    raise NotImplementedError
