import pytest
from fastapi import HTTPException

from api.validators import sanitize_target_value, validate_password_strength


# ── email ──────────────────────────────────────────────────────────────────

def test_email_valid_and_lowercased():
    assert sanitize_target_value("email", "User@Example.COM") == "user@example.com"

def test_email_invalid_raises():
    with pytest.raises(HTTPException, match="Invalid email"):
        sanitize_target_value("email", "not-an-email")


# ── ip / SSRF ──────────────────────────────────────────────────────────────

def test_ip_public_accepted():
    assert sanitize_target_value("ip", "8.8.8.8") == "8.8.8.8"

@pytest.mark.parametrize("blocked_ip", [
    "127.0.0.1",       # loopback
    "10.0.0.1",        # RFC 1918
    "192.168.1.1",     # RFC 1918
    "172.16.0.1",      # RFC 1918
    "169.254.1.1",     # link-local
    "::1",             # IPv6 loopback
])
def test_ip_private_ranges_blocked(blocked_ip):
    with pytest.raises(HTTPException, match="Private"):
        sanitize_target_value("ip", blocked_ip)

def test_ip_invalid_raises():
    with pytest.raises(HTTPException, match="Invalid IP"):
        sanitize_target_value("ip", "999.999.999.999")


# ── domain ─────────────────────────────────────────────────────────────────

def test_domain_valid_and_lowercased():
    assert sanitize_target_value("domain", "Example.COM") == "example.com"

@pytest.mark.parametrize("bad_domain", [
    "https://example.com",   # protocol prefix
    "example.com/path",      # path included
    "user@example.com",      # credentials
])
def test_domain_invalid_raises(bad_domain):
    with pytest.raises(HTTPException):
        sanitize_target_value("domain", bad_domain)


# ── username ───────────────────────────────────────────────────────────────

def test_username_valid():
    assert sanitize_target_value("username", "bianca_oliveira") == "bianca_oliveira"

def test_username_with_space_raises():
    with pytest.raises(HTTPException):
        sanitize_target_value("username", "bianca oliveira")


# ── phone ──────────────────────────────────────────────────────────────────

def test_phone_strips_formatting():
    assert sanitize_target_value("phone", "+55 (27) 99999-9999") == "5527999999999"

def test_phone_too_short_raises():
    with pytest.raises(HTTPException, match="phone"):
        sanitize_target_value("phone", "123")


# ── common guards ──────────────────────────────────────────────────────────

def test_empty_value_raises():
    with pytest.raises(HTTPException, match="empty"):
        sanitize_target_value("email", "   ")

def test_value_exceeding_max_length_raises():
    with pytest.raises(HTTPException, match="maximum length"):
        sanitize_target_value("username", "a" * 300)


# ── password strength ──────────────────────────────────────────────────────

def test_strong_password_passes():
    validate_password_strength("Str0ng!Password#2024")  # should not raise

@pytest.mark.parametrize("weak_password, expected_fragment", [
    ("short1!A",          "12 characters"),
    ("alllowercase1!",    "uppercase"),
    ("ALLUPPERCASE1!",    "lowercase"),
    ("NoDigitsHere!!",    "digit"),
    ("NoSpecialChars1",   "special character"),
])
def test_weak_password_raises(weak_password, expected_fragment):
    with pytest.raises(HTTPException, match=expected_fragment):
        validate_password_strength(weak_password)
