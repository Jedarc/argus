import ipaddress
import re
from typing import Literal

from fastapi import HTTPException, status

TargetType = Literal["username", "email", "phone", "ip", "domain", "name"]

_MAX_TARGET_LENGTH = 256
_MIN_PASSWORD_LENGTH = 12

# RFC 5321 / 5322 — simplified but strict enough for our purposes
_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

# Hostnames per RFC 1123
_DOMAIN_PATTERN = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
)

# Printable ASCII only, no whitespace — covers most platform username rules
_USERNAME_PATTERN = re.compile(r"^[\x21-\x7E]{1,100}$")

# Allow Unicode letters, spaces, hyphens, apostrophes, dots — covers international names
_NAME_PATTERN = re.compile(r"^[\w\s'\-\.]{2,120}$", re.UNICODE)

# Digits only after stripping formatting characters
_PHONE_DIGITS_PATTERN = re.compile(r"^\d{7,15}$")

# Private and reserved IP ranges — blocked to prevent SSRF
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),
    ipaddress.ip_network("240.0.0.0/4"),
    ipaddress.ip_network("255.255.255.255/32"),
    # IPv6
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("ff00::/8"),
]


def _unprocessable(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


def _assert_not_private_ip(address: str) -> None:
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        return
    for network in _BLOCKED_NETWORKS:
        if parsed in network:
            raise _unprocessable("Private, loopback, and reserved IP addresses are not allowed")


def sanitize_target_value(target_type: TargetType, raw_value: str) -> str:
    """
    Validates and normalizes a target value for the given type.
    Raises HTTP 422 on any invalid or disallowed input.
    Always call this before persisting or passing to a module.
    """
    value = raw_value.strip()

    if not value:
        raise _unprocessable("Target value cannot be empty")

    if len(value) > _MAX_TARGET_LENGTH:
        raise _unprocessable(f"Target value exceeds maximum length of {_MAX_TARGET_LENGTH} characters")

    if target_type == "email":
        if not _EMAIL_PATTERN.match(value):
            raise _unprocessable("Invalid email address format")
        return value.lower()

    if target_type == "ip":
        try:
            parsed = ipaddress.ip_address(value)
        except ValueError:
            raise _unprocessable("Invalid IP address")
        _assert_not_private_ip(value)
        return str(parsed)

    if target_type == "domain":
        if value.startswith(("http://", "https://", "//")):
            raise _unprocessable("Domain must not include a protocol prefix")
        if "/" in value or "@" in value or " " in value:
            raise _unprocessable("Domain must not include a path, credentials, or spaces")
        if not _DOMAIN_PATTERN.match(value):
            raise _unprocessable("Invalid domain name")
        return value.lower()

    if target_type == "username":
        if not _USERNAME_PATTERN.match(value):
            raise _unprocessable(
                "Username must be 1–100 printable ASCII characters with no spaces"
            )
        return value

    if target_type == "phone":
        digits_only = re.sub(r"[\s\-\(\)\+\.]", "", value)
        if not _PHONE_DIGITS_PATTERN.match(digits_only):
            raise _unprocessable("Invalid phone number — must contain 7 to 15 digits")
        return digits_only

    if target_type == "name":
        if not _NAME_PATTERN.match(value):
            raise _unprocessable("Name contains invalid characters or is outside the 2–120 character range")
        return " ".join(value.split())  # normalise internal whitespace

    raise _unprocessable(f"Unknown target type: {target_type}")


def validate_password_strength(password: str) -> None:
    """
    Enforces minimum password requirements for the setup and change-password flows.
    Raises HTTP 422 with a descriptive message on failure.
    """
    if len(password) < _MIN_PASSWORD_LENGTH:
        raise _unprocessable(
            f"Password must be at least {_MIN_PASSWORD_LENGTH} characters long"
        )
    if not re.search(r"[A-Z]", password):
        raise _unprocessable("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise _unprocessable("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise _unprocessable("Password must contain at least one digit")
    if not re.search(r"[^a-zA-Z0-9]", password):
        raise _unprocessable("Password must contain at least one special character")
